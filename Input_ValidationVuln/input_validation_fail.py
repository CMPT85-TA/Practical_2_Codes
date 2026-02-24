import sqlite3
from flask import Flask, request

app = Flask(__name__)


# Connect to an SQLite database (for simplicity)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create a sample table
# cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')

# Let's say this function is used to authenticate users
def authenticate_user(username, password):
    # No sanitization of input!
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        query = f"SELECT id FROM users WHERE username='{username}' AND password='{password}'"
        print(query)
        cursor.execute(query)
        return cursor.fetchall()

@app.route('/login', methods=['POST'])
def comment_page():
    data = request.get_json()
    # Fetch comment from user input directly without sanitizing
    if len(authenticate_user(data['username'], data['password'])):
        return f"<html><body>Logged In</body></html>"
    return "<html><body>No hacking!!!</body></html>"

app.run(port=5000)
