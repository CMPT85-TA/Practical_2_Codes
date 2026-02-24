# Audit Logging: vulnerable vs fixed example

Short instructions to create a Python environment, install requirements, run the vulnerable and fixed apps, and inspect the logs.

## Requirements
- Python 3.8+ (Linux)
- A terminal with bash

## Create a virtual environment
1. Create and activate a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies (Flask is required):

```bash
pip install Flask
# Or to create a requirements file for later reproducibility:
echo "Flask" > requirements.txt
pip install -r requirements.txt
```

## Run the vulnerable app
Open terminal window 1 and run:

```bash
python3 too_much_logging.py 2>&1 | tee server.log
```

In terminal window 2, trigger a purchase:

```bash
curl -s -X POST http://127.0.0.1:5000/make_purchase \
  -H "Content-Type: application/json" \
  -d '{"cc_number":"4111 1111-1111 1111"}'

cat server.log
```

Expected (vulnerable) log contains the full credit-card number, for example:

```
ERROR:root:Customer made a purchase with CC number 4111 1111-1111 1111
```

## Run the fixed app
Stop the vulnerable server (Ctrl+C in window 1) and then in window 1 run:

```bash
python3 too_much_logging-fix.py 2>&1 | tee server.log
```

Repeat the same curl request in window 2 and inspect `server.log`:

```bash
curl -s -X POST http://127.0.0.1:5000/make_purchase \
  -H "Content-Type: application/json" \
  -d '{"cc_number":"4111 1111-1111 1111"}'

cat server.log
```

Expected (fixed) log masks the card number and only shows the last 4 digits, for example:

```
ERROR:root:Customer made a purchase with missing cc_number: *************-1111
```

## Short difference between the two files
- `too_much_logging.py` (vulnerable): logs the entire `cc_number` value directly. This exposes sensitive cardholder data in logs.
- `too_much_logging-fix.py` (fixed): only logs a masked value showing the last 4 digits. This reduces sensitive data exposure in logs.

## Security note
Never log full card numbers, CVVs, or other sensitive payment data. Keep logs minimal, use masking or tokenization, and protect access to log storage.
