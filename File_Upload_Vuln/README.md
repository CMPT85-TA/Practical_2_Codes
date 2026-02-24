# File Upload Demo (insecure vs secure)

This repository contains two small Flask demos to illustrate an insecure file upload implementation and a more secure alternative.

This README shows how to create a Python virtual environment, install dependencies, run each app, and manually verify the insecure behavior (path traversal / filename trust) and the corresponding protections in the secure app.

## Quick overview

- `file_upload_insecure.py` — saves uploaded files using the user-supplied filename with no validation. This is vulnerable to path traversal and can overwrite arbitrary files the server process can write.
- `file_upload_secure.py` — demonstrates a safer approach:
  - max upload size (10 MiB)
  - uses `python-magic` (libmagic) to sniff the real MIME type
  - allow-list for MIME types (PDF only in this demo)
  - checks extension as defense-in-depth
  - generates UUID filenames and uses a `safe_join` to prevent traversal

## Environment and dependencies

These instructions assume Linux (Ubuntu/Debian) or macOS. On Windows, adjust the system dependency step and prefer `python-magic-bin` if necessary.

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the system libmagic library (required by `python-magic`) — Linux / macOS:

```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y libmagic1

# macOS (Homebrew)
brew install libmagic
```

On Windows, you can try `pip install python-magic-bin` instead of `python-magic`.

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

If you prefer to avoid `python-magic` for now, you can still run the insecure demo; the secure demo will fail with a clear message asking you to install `python-magic`.

## Run the apps

Start each app in its own shell (they bind to different ports):

```bash
# insecure: port 5001
python3 file_upload_insecure.py

# secure: port 5002
python3 file_upload_secure.py
```

Open the pages at http://127.0.0.1:5001/ and http://127.0.0.1:5002/ to manually upload files via the browser, or use the curl examples below.

## Test steps 

The following curl commands show how to reproduce the insecure behavior and verify the secure app blocks or mitigates it. Use these from a different terminal while the respective app is running.

1) Demonstrate path traversal / filename trust in the insecure app

Create a small payload file locally first:

```bash
printf "pwned" > payload.txt
```

Upload it to the insecure app while setting a traversal filename (the app will trust this name and try to write there):

```bash
curl -v -F "file=@payload.txt;filename=../../tmp/hacked.txt" http://127.0.0.1:5001/upload
```

What to check:
- If the server process has permission, `/tmp/hacked.txt` will be created (or overwritten) with the contents of `payload.txt`. Verify with:

```bash
ls -l /tmp/hacked.txt && cat /tmp/hacked.txt
```

This shows the server trusted the user-supplied filename and allowed a write outside the intended `uploads_insecure` directory.

2) Attempt the same on the secure app (should NOT write to `/tmp`)

Try to upload the same `payload.txt` but to the secure app, again setting a traversal filename and a `.pdf` extension to try to trick it:

```bash
curl -v -F "file=@payload.txt;filename=../../tmp/evil.pdf" http://127.0.0.1:5002/upload
```

Expected results:
- If `python-magic` is installed and correctly detects the file as a non-PDF, the secure app will reject the upload with HTTP 400 (invalid MIME type).
- If you use a real PDF file (for example `sample.pdf`) and upload that with a traversal filename:

```bash
curl -v -F "file=@sample.pdf;filename=../../tmp/evil.pdf" http://127.0.0.1:5002/upload
```

Then the secure app should accept the upload but save it using an internal UUID filename inside the `uploads_secure` directory — it will not create `/tmp/evil.pdf`. Verify with:

```bash
ls -l uploads_secure
```

The JSON response from the secure app includes the `saved_as` value (the UUID filename) and the detected `mime`.

Notes on MIME testing:
- For a reliable test of acceptance, use a real PDF file for `sample.pdf` (download a small PDF or use one you have). Minimal handcrafted PDF-like headers may not be sufficient for `libmagic` to classify the file as `application/pdf`.

## Short difference summary

- Insecure: trusts user-supplied filename (allows path traversal), no MIME/type checks, no explicit size limits.
- Secure: enforces `MAX_CONTENT_LENGTH`, sniffs MIME with `libmagic`, enforces an allow-list, checks extension, ignores the user filename (uses UUID), and prevents traversal with `safe_join`.