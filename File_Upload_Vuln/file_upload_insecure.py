# app_insecure.py
from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

UPLOAD_DIR = "uploads_insecure"
os.makedirs(UPLOAD_DIR, exist_ok=True)

PAGE = """
<!doctype html>
<title>Insecure Upload</title>
<h1>Insecure Upload</h1>
<form method="post" action="/upload" enctype="multipart/form-data">
  <input type="file" name="file">
  <button type="submit">Upload</button>
</form>
<p>Files are saved using your provided filename without validation.</p>
"""

@app.get("/")
def index():
    return render_template_string(PAGE)

@app.post("/upload")
def upload():
    f = request.files.get("file")
    if not f:
        return "no file", 400

    # ❌ Insecure: trusts user-supplied filename
    # ❌ No type validation
    # ❌ No size limits beyond OS limits
    # ❌ Vulnerable to path traversal & overwrite
    path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(path)

    return f"Saved (INSECURE) to: {path}\n"

if __name__ == "__main__":
    app.run(port=5001, debug=True)
