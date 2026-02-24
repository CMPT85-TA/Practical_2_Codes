import secrets
from urllib.parse import urlparse
from flask import Flask, request, session, redirect, url_for, abort

app = Flask(__name__)
app.secret_key = "dev-only-not-secret"
transactions = []

# Harden cookies (in production also set SESSION_COOKIE_SECURE = True behind HTTPS)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

def require_login():
    if not session.get("user"):
        abort(401, "Not logged in")

def same_origin(origin_header: str, expected_origin: str) -> bool:
    try:
        o = urlparse(origin_header)
        return f"{o.scheme}://{o.netloc}" == expected_origin
    except Exception:
        return False

def verify_csrf():
    # 1) Origin/Referer check
    expected_origin = request.host_url.rstrip("/")
    origin = request.headers.get("Origin") or ""
    referer = request.headers.get("Referer") or ""
    if origin:
        if not same_origin(origin, expected_origin):
            abort(403, "Bad Origin")
    elif referer:
        if not referer.startswith(expected_origin):
            abort(403, "Bad Referer")
    else:
        # No Origin or Referer? Treat as suspicious.
        abort(403, "Missing CSRF context")

    # 2) Token check (form field or header)
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    if not sent or sent != session.get("csrf_token"):
        abort(403, "Invalid CSRF token")

@app.after_request
def security_headers(resp):
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/")
def home():
    if not session.get("user"):
        return """
        <h2>Welcome to MyBank (secure)</h2>
        <p><a href="/login">Login as alice</a></p>
        """
    # Issue CSRF token per session (rotate as you like)
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    token = session["csrf_token"]
    return f"""
    <h2>Hello, {session['user']}</h2>
    <p>Secure transfer: POST only + CSRF token + Origin check.</p>
    <form action="/transfer" method="POST">
      <input type="hidden" name="csrf_token" value="{token}">
      <label>Beneficiary:</label><input name="beneficiary_account" value="45047580936"><br>
      <label>Amount:</label><input name="amount" value="100000"><br>
      <button type="submit">Send</button>
    </form>
    <p><a href="/transactions">View transactions</a> | <a href="/logout">Logout</a></p>
    """

@app.route("/login")
def login():
    session.clear()
    session['user'] = 'alice'
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

# SECURE: POST only + CSRF + Origin/Referer validation
@app.route("/transfer", methods=["POST"])
def transfer_secure():
    require_login()
    verify_csrf()

    acct = request.form.get("beneficiary_account")
    amount = request.form.get("amount")
    if not acct or not amount:
        return "Missing fields", 400

    transactions.append({
        "by": session["user"],
        "to": acct,
        "amount": amount,
        "via": "POST"
    })
    return "✅ Secure transfer scheduled."

@app.route("/transactions")
def txns():
    require_login()
    html = "<h2>Transactions</h2><ul>"
    for t in transactions:
        html += f"<li>{t['by']} → {t['to']} : {t['amount']} (via {t['via']})</li>"
    html += "</ul><p><a href='/'>Home</a></p>"
    return html

if __name__ == "__main__":
    app.run(port=5001, debug=True)
