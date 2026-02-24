## Session Management: quick test & setup

This repo contains two example Flask apps demonstrating a session-management weakness (`session_management-fail.py`) and a fixed variant (`session_management-fix.py`). This short README shows how to create a Python environment, install dependencies, set the required environment variables on Ubuntu, and run the tests you outlined.

### Prerequisites
- Ubuntu / Linux
- Python 3.8+
- git (optional)

### 1) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Environment variables (Ubuntu shell)
Export a strong Flask secret and the static salt for the fixed server session handling. Run these in the same shell where you will start the fixed app.

```bash
# generate a random 32-byte hex secret for Flask signing
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# static salt used by the app (kept secret in production)
export STATIC_SALT="STATIC_SALT"
```

Note: for the vulnerable server you do not need to set these (it uses a hard-coded secret in the vulnerable example). For the fixed server, `SECRET_KEY` must be set to a secret unknown to an attacker.

### 3) Install requirements (already above)
```bash
pip install -r requirements.txt
```

### 4) Testing the vulnerable app (prove auth bypass)
Open a terminal (with venv activated) and run:

```bash
python session_management-fail.py
# server runs on http://127.0.0.1:5000
```

Sanity check: normal login (saves cookie to `jar`):

```bash
curl -c jar -X POST http://127.0.0.1:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}'

curl -i -b jar http://127.0.0.1:5000/me
```

Forge a valid Flask session cookie without logging in (this uses `make_cookie.py` present in the repo):

```bash
COOKIE=$(python make_cookie.py)
echo "$COOKIE"

# Use the forged cookie to access /me
curl -i -H "Cookie: session=$COOKIE" http://127.0.0.1:5000/me
# Expected: 200 OK and `OK: <md5>`
```

If you see `No session`, try warming the server and retrying:

```bash
curl -s http://127.0.0.1:5000/login -o /dev/null
curl -i -H "Cookie: session=$COOKIE" http://127.0.0.1:5000/me
```

### 5) Testing the fixed app (forge should fail)
In a new terminal (or same terminal after setting env vars), ensure `SECRET_KEY` and `STATIC_SALT` are exported (see step 2). Then run:

```bash
python session_management-fix.py
# server runs on http://127.0.0.1:5000
```

Normal login still works (saves cookie to `jar`):

```bash
curl -c jar -X POST http://127.0.0.1:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}'

curl -i -b jar http://127.0.0.1:5000/me
# Expected: 200 (and inspect body for session contents)
```

Try using the previously forged cookie from the vulnerable app (reuse `COOKIE`):

```bash
curl -i -H "Cookie: session=$COOKIE" http://127.0.0.1:5000/me
# Expected: 401 or Flask rejects the forged cookie (signature mismatch)
```

### Differences between `session_management-fail.py` and `session_management-fix.py`
- `session_management-fail.py`:
  - Uses a hard-coded `SECRET_KEY` (e.g. `'my_secret_key'`) so an attacker who knows the secret (or who can reproduce its signing) can forge cookies.
  - Uses a hard-coded static salt string inside the code when deriving the `user_id`.
  - This combination enables forging a Flask session cookie (the repo includes `make_cookie.py` to demonstrate forging).

- `session_management-fix.py`:
  - Reads `SECRET_KEY` from the environment. If you set a strong random `SECRET_KEY`, Flask's cookie signatures cannot be forged by an attacker who doesn't know that secret.
  - Reads `STATIC_SALT` from the environment so the salt is not necessarily the same on all deployments.
  - The practical security improvement here is that a strong, unguessable `SECRET_KEY` prevents attackers from producing valid signed cookies offline even if they can guess how session payloads are constructed.

Note: an additional improvement (not fully implemented here) is to avoid storing predictable IDs derived from usernames and salts in the session. Prefer storing the username or a securely generated random session identifier mapped server-side to session data.
