from flask import Flask, request, session, redirect, url_for, make_response

app = Flask(__name__)
app.secret_key = "dev-only-not-secret"
transactions = []

@app.after_request
def add_headers(resp):
    # INTENTIONALLY LAX (default) so the GET-CSRF demo works naturally.
    # NOTE: do NOT copy this pattern to real apps.
    resp.headers['Cache-Control'] = 'no-store'
    return resp

@app.route("/")
def home():
    if not session.get("user"):
        return """
        <h2>Welcome to MyBank</h2>
        <p><a href="/login">Login as alice</a></p>
        """
    return f"""
    <h2>Hello, {session['user']}</h2>
    <p>Legit transfer form (INSECURE ON PURPOSE): this uses GET and has NO CSRF.</p>
    <form action="/transfer" method="GET">
      <label>Beneficiary:</label><input name="beneficiary_account" value="45047580936"><br>
      <label>Amount:</label><input name="amount" value="100000"><br>
      <button type="submit">Send</button>
    </form>
    <p><a href="/transactions">View transactions</a> | <a href="/logout">Logout</a></p>
    """

@app.route("/login")
def login():
    session['user'] = 'alice'
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

# INTENTIONALLY VULNERABLE: allows GET (state change) and no CSRF
@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if not session.get("user"):
        return "Not logged in", 401

    # Accepts params from either query string or form
    acct = request.values.get("beneficiary_account")
    amount = request.values.get("amount")
    if not acct or not amount:
        return "Missing fields", 400

    transactions.append({
        "by": session["user"],
        "to": acct,
        "amount": amount,
        "via": request.method
    })
    return f"✅ Transfer scheduled: {amount} to {acct} (via {request.method})"

@app.route("/transactions")
def txns():
    if not session.get("user"):
        return "Not logged in", 401
    html = "<h2>Transactions</h2><ul>"
    for t in transactions:
        html += f"<li>{t['by']} → {t['to']} : {t['amount']} (via {t['via']})</li>"
    html += "</ul><p><a href='/'>Home</a></p>"
    return html

if __name__ == "__main__":
    app.run(port=5000, debug=True)
