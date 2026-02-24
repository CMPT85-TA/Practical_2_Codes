# app_secure.py
from flask import Flask, request, render_template_string, abort, jsonify
import os, uuid

app = Flask(__name__)

# Hard max (Flask returns 413 if exceeded)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MiB

UPLOAD_DIR = "uploads_secure"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Strong type sniffing with libmagic ---
# Linux/macOS: `sudo apt-get install -y libmagic1` or `brew install libmagic`
# Then: `pip install python-magic`
# Windows: `pip install python-magic-bin`
try:
    import magic
    def sniff_mime(buf: bytes) -> str:
        return magic.from_buffer(buf, mime=True)
except ImportError as e:
    raise SystemExit(
        "python-magic is required for this demo.\n"
        "Install on Linux/macOS: pip install python-magic (and libmagic via apt/brew)\n"
        "Install on Windows: pip install python-magic-bin\n"
        f"Import error: {e}"
    )

ALLOWED_MIME = {"application/pdf"}
ALLOWED_EXTS = {".pdf"}

PAGE = """
<!doctype html>
<title>Secure Upload</title>
<h1>Secure Upload</h1>
<form method="post" action="/upload" enctype="multipart/form-data">
  <input type="file" name="file" />
  <button type="submit">Upload</button>
</form>
<ul>
  <li>Sniffs real MIME with libmagic</li>
  <li>Allow-list: application/pdf (+ .pdf extension)</li>
  <li>UUID filenames (ignore user filename)</li>
  <li>Blocks path traversal; 10 MiB size cap</li>
</ul>
"""

def safe_join(root: str, leaf: str) -> str:
    """Ensure the final path stays within root (prevents traversal)."""
    root_abs = os.path.abspath(root) + os.sep
    full = os.path.abspath(os.path.join(root, leaf))
    if not full.startswith(root_abs):
        raise ValueError("Path traversal detected")
    return full

@app.get("/")
def index():
    return render_template_string(PAGE)

@app.post("/upload")
def upload():
    f = request.files.get("file")
    if not f:
        return "no file", 400

    # Read small header and sniff true type
    head = f.stream.read(4096)
    f.stream.seek(0)
    real_mime = sniff_mime(head)

    # Enforce allow-list
    if real_mime not in ALLOWED_MIME:
        abort(400, description=f"Invalid file type: {real_mime}")

    # Check extension (defense in depth)
    ext = os.path.splitext(f.filename or "")[1].lower()
    if ext not in ALLOWED_EXTS:
        abort(400, description="Extension must be .pdf")

    # Use our own filename (don’t trust user input)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    path = safe_join(UPLOAD_DIR, safe_name)

    f.save(path)
    return jsonify({"saved_as": safe_name, "mime": real_mime})

if __name__ == "__main__":
    app.run(port=5002, debug=True)
