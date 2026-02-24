# Input Validation Demo — README

This short README shows how to create a Python environment, install requirements, perform the initial database setup and migration (the two "windows" you described), run the vulnerable and fixed apps, and test them with curl. It also explains the difference between the two files in this repo: `input_validation_fail.py` and `input_validation_fix.py`.

## 1) Create a Python environment

1. From the project directory, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Upgrade pip (optional but recommended):

```bash
pip install --upgrade pip
```

## 2) Install the requirements

Install the minimal packages needed to run the sample Flask apps and (optionally) password hashing utilities:

```bash
pip install flask werkzeug
```

If you prefer a `requirements.txt`, create one with:

```
flask
werkzeug
```

and then install with `pip install -r requirements.txt`.

## 3) Initial database setup (window1)

This creates a small SQLite database with a `users` table that stores a plaintext password for a demo user `alice`.

Open a Python REPL and run the following (or copy-paste into a one-off `python3` session):

```python
import sqlite3
with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    c.execute("INSERT INTO users(username, password) VALUES (?,?)", ("alice", "p@ssw0rd"))
    conn.commit()
```

After that, start the vulnerable app in a separate terminal:

```bash
python3 input_validation_fail.py
```

## 4) Test the vulnerable app (window2 testing)

Use curl to test a normal login and two SQL-injection attempts:

Normal login (should return "Logged In"):

```bash
curl -s -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"p@ssw0rd"}'
```

SQL injection attempt #1 (payload injected into username):

```bash
curl -s -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice' -- ","password":"whatever"}'
```

SQL injection attempt #2 (classic OR payload):

```bash
curl -s -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"' OR 1=1 -- ","password":"x"}'
```

The vulnerable server (`input_validation_fail.py`) uses string formatting to build the SQL query and is expected to be bypassable by such inputs.

## 5) Migrate to hashed passwords + run fixed app

To migrate the database to use a hashed password column and seed `alice` with a hashed password, run a one-off Python snippet that uses Werkzeug's `generate_password_hash`:

```python
import sqlite3
from werkzeug.security import generate_password_hash
with sqlite3.connect("database.db") as conn:
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT NOT NULL)")
    c.execute("INSERT INTO users(username, password_hash) VALUES (?, ?)",
              ("alice", generate_password_hash("p@ssw0rd")))
    conn.commit()
```

Then start the fixed app in a separate terminal:

```bash
python3 input_validation_fix.py
```

## 6) Test the fixed app

Re-run the same three curl commands above against the running fixed server. The fixed app uses parameterized SQL queries to avoid SQL injection; it should not be tricked by the injection payloads.

If you migrated to `password_hash` (as shown above), the fixed app should also verify the password by comparing the provided password against the hash (using `check_password_hash`) — see Notes below for verification and small hardening tips.

## 7) Quick differences between the two files

- `input_validation_fail.py`:
  - Builds SQL queries by injecting user input directly into a formatted string (e.g., an f-string). Example: `query = f"SELECT id FROM users WHERE username='{username}' AND password='{password}'"`.
  - This allows user-supplied values to break out of the intended query structure and perform SQL injection (e.g., `"' OR 1=1 -- "`).
  - Uses plaintext password storage in the database (the initial setup creates a `password` column that stores raw passwords).

- `input_validation_fix.py`:
  - Uses parameterized queries with `?` placeholders and passes user values as a tuple to `cursor.execute(...)`. This prevents SQL injection because the DB driver treats the inputs as data, not SQL syntax.
  - After the migration step (if you created a `password_hash` column and stored hashes with `generate_password_hash`), the fix should also perform password verification using `check_password_hash` rather than comparing plaintext passwords.

Security impact: parameterized queries stop SQL injection; hashed + salted password storage prevents password disclosure from DB leaks and avoids storing raw passwords.