# Auth Bypass Vulnerability — Test Instructions

This repository contains two PHP scripts for demonstrating an authentication-bypass vulnerability and its fix.

Files in this folder:

- `auth_bypass_vuln.php` — vulnerable example
- `auth_bypass_fix.php` — fixed version (note: older instructions may refer to `fixed.php`)

## Prerequisites

- PHP (8.x recommended) with the built-in web server available (`php -S`).
- curl (for sending the test requests).

Install on common systems:

- Debian / Ubuntu:

```bash
sudo apt update
sudo apt install -y php-cli curl
```

- Fedora / CentOS (dnf):

```bash
sudo dnf install -y php-cli curl
```

- macOS (Homebrew):

```bash
brew install php curl
```

- Windows:

Use the official PHP Windows builds (https://windows.php.net/) or use XAMPP / WampServer.

## Running the tests

Open two terminal windows.

Window 1 — start the PHP built-in server from this repository root (where the PHP files live):

```bash
php -S 127.0.0.1:8000
```

Leave that running (Ctrl-C to stop).

Window 2 — run the curl requests to exercise the vulnerable and fixed endpoints.

Vulnerable script (`auth_bypass_vuln.php`):

```bash
curl -i -X POST \
  -d 'color[color]=x' \
  -d 'color[credentials]=' \
  http://127.0.0.1:8000/auth_bypass_vuln.php
```

Fixed script (`auth_bypass_fix.php`):

```bash
curl -i -X POST \
  -d 'color[color]=x' \
  -d 'color[credentials]=' \
  http://127.0.0.1:8000/auth_bypass_fix.php
```

## What to look for

- Compare the HTTP response headers and body returned by the vulnerable and fixed endpoints.
- In the vulnerable version you may see behavior that indicates the authentication check was bypassed when `color[credentials]` is empty or specially crafted.
- The fixed version should not allow unauthorized access and should respond with an appropriate error or redirect.

## Troubleshooting

- If `php -S` fails, ensure you're in the directory that contains the PHP files.
- If curl returns `Connection refused`, verify the server is running and listening on 127.0.0.1:8000.
- For more verbose curl output add `-v` to the curl commands.

## Security note

These scripts are for educational purposes only. Do not deploy vulnerable code to a production environment.

---
