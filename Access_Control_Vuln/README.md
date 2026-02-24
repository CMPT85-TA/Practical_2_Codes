## Quick start (clear and minimal)

Purpose: show how a simple path-based access check can be bypassed when routing is case-insensitive, and how enabling Express case-sensitive routing fixes it.

1) Install dependencies (run in this folder):

```bash
npm install
```

2) Start the vulnerable server (Terminal A):

```bash
node access_control_vulnerability_vulnerable.js
```

3) Test in another terminal (Terminal B):

```bash
curl -i -H "Authorization: Bearer good" http://localhost:4242/secret
curl -i -H "Authorization: Bearer good" http://localhost:4242/Secret
```

4) Stop the vulnerable server (Ctrl+C in Terminal A). Start the fixed server:

```bash
node access_control_vulnerability_fixed.js
```

5) Re-run the two curl commands above. Expected result: vulnerable server accepts both `/secret` and `/Secret`; fixed server returns 404 for `/Secret`.

Files (one-line purpose each):
- `access_control_vulnerability_vulnerable.js` — demo server with a path-based check that can be bypassed by case differences.
- `access_control_vulnerability_fixed.js` — same demo but enables Express case-sensitive routing to prevent the bypass.
- `authentication.js` — minimal token-check helper used by both servers (checks Authorization header).
- `secret.js` — the protected router that returns the secret JSON response when authorized.