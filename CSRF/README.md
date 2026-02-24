## MyBank CSRF demo

This small demo contains two minimal Flask apps showing a Cross-Site Request Forgery (CSRF) vulnerability and a fixed version.

Files:
- `bank_csrf_vuln.py` — intentionally vulnerable demo (runs on port 5000).
- `bank_secure_csrf.py` — secure demo with POST-only transfer, CSRF token, and origin checks (runs on port 5001).
- `attacker_link.html` and `attacker_autopost.html` — example attacker pages used to demonstrate the vulnerability.

## Requirements
- Python 3.8+ (3.8/3.9/3.10 should work)
- pip

You only need Flask to run the demos. Create a virtual environment and install Flask:

```bash
python3 -m venv venv
source venv/bin/activate
pip install Flask
# (optional) save requirements
pip freeze > requirements.txt
```

Or create a minimal `requirements.txt` with:

```text
Flask
```
and then run `pip install -r requirements.txt`.

## Run the vulnerable app (manual test)

1. Start the vulnerable server:

```bash
source venv/bin/activate
python bank_csrf_vuln.py
```

2. In a browser open: http://localhost:5000
3. Click "Login as alice".
4. On the home page you'll see a transfer form that submits via GET (intentionally insecure).
5. To demonstrate a naive GET-CSRF: open `attacker_link.html` (double-click the file or open it in a new tab). When the victim (you) clicks the link while still logged in to the vulnerable app, the bank will process the transfer because the vulnerable endpoint accepts state-changing GET requests and no CSRF checks are performed.

6. To demonstrate an auto-submitting attack: open `attacker_autopost.html` in a separate tab while still logged in to the vulnerable app. The page will auto-submit a transfer form to `http://localhost:5000/transfer` (the vulnerable app accepts it because no token or origin checks are required).

7. View transactions at: http://localhost:5000/transactions — you should see the injected transfer(s).

Expected: The vulnerable app will accept both the link (GET) and the auto-post (POST) because it performs no CSRF protection and accepts state changes via GET.

## Run the secure app (manual test)

1. Stop the vulnerable server if it's still running, then start the secure server:

```bash
source venv/bin/activate
python bank_secure_csrf.py
```

2. In a browser open: http://localhost:5001
3. Click "Login as alice".
4. On the home page there's a transfer form that submits via POST and contains a hidden `csrf_token`.

Manual test of attack pages (expected behavior):
- Open `attacker_link.html`: this does a top-level GET to `http://localhost:5001/transfer` — the secure server only accepts POST, so the GET should fail.
- Open `attacker_autopost.html`: this auto-posts from a `file://` origin (or the attacker's origin). The secure server checks Origin/Referer and requires a session CSRF token. Since the attacker page cannot know the victim's token and will present no valid Origin/Referer, the secure app will reject the request (403).

3. View transactions at: http://localhost:5001/transactions — the attack attempts should not appear.

## Short difference summary

- `bank_csrf_vuln.py` (vulnerable):
  - Accepts state-changing requests via GET (and POST) from any origin.
  - No CSRF token is required.
  - No Origin/Referer checks.
  - Cookies default (no SAMESITE/HTTPONLY set in this demo).

- `bank_secure_csrf.py` (fixed):
  - Only accepts POST for the transfer endpoint.
  - Issues a per-session CSRF token and requires it in the form (or X-CSRF-Token header).
  - Performs Origin/Referer validation.
  - Sets `SESSION_COOKIE_HTTPONLY=True` and `SESSION_COOKIE_SAMESITE='Lax'` in the app config and adds some security headers.

Together these measures prevent trivial CSRF attacks from attacker pages that cannot read the victim's token or originate from the same origin.
