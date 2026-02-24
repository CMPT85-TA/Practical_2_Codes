from flask import Flask, session, request, redirect, url_for
import hashlib
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
static_salt = str(os.getenv('STATIC_SALT'))

users = {'alice': 'password123'}  # A mock database

@app.route('/login', methods=['POST'])
def login():
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    
    if users.get(username) == password:
        # Creating a predictable session ID using username and a static string
        session_id = hashlib.md5((username + static_salt).encode()).hexdigest()
        session['user_id'] = session_id
        
        return f"<html><body>Logged in with session id {session['user_id']}</body></html>"
    return "Login failed!", 401

@app.route('/me')
def me():
    return ('OK: ' + session['user_id'], 200) if 'user_id' in session else ('No session', 401)


app.run(port=5000)
