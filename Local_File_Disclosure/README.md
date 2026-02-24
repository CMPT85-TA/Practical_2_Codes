# Local File Disclosure demo (Rust + Actix Web)

Two small servers show a local file disclosure issue and a safe configuration. Both serve a demo page and a static files mount at `/public` on port 8888.

## Folders
- `local_file_disclosure_server-vuln`: Vulnerable configuration. Static root is set to the project directory (`.`), so unintended files can be fetched.
- `local_file_disclosure_server-fix`: Fixed configuration. Static root is limited to `./static`, so files outside that folder are not served.

## Requirements
- Linux, macOS, or Windows with a POSIX-like shell
- Rust toolchain (rustup, cargo) — https://rustup.rs

## Run the vulnerable server
1. Open a terminal and run:
   ```bash
   cd local_file_disclosure_server-vuln
   cargo run
   ```
2. In another terminal, verify behavior:
   - Demo page:
     ```bash
     curl -i http://127.0.0.1:8888/
     ```
   - Static image (expected 200):
     ```bash
     curl -i http://127.0.0.1:8888/public/static/polygons.jpg
     ```
   - Sensitive file disclosure (expected 200, shows secret):
     ```bash
     curl -i http://127.0.0.1:8888/public/sensitive.txt
     ```
   - Path traversal also reaches the file (expected 200):
     ```bash
     curl -i http://127.0.0.1:8888/public/../sensitive.txt
     ```
3. Stop the server with Ctrl+C.

## Run the fixed server
1. Open a terminal and run:
   ```bash
   cd local_file_disclosure_server-fix
   cargo run
   ```
2. In another terminal, verify behavior:
   - Demo page:
     ```bash
     curl -i http://127.0.0.1:8888/
     ```
   - Static image (expected 200):
     ```bash
     curl -i http://127.0.0.1:8888/public/polygons.jpg
     ```
   - Sensitive file should NOT be served (expected 404/403/400):
     ```bash
     curl -i http://127.0.0.1:8888/public/sensitive.txt
     curl -i http://127.0.0.1:8888/public/../sensitive.txt
     ```
3. Stop the server with Ctrl+C.

## Tests
- Each project has tests under `tests/`.
- Run tests per project:
  ```bash
  cd local_file_disclosure_server-vuln && cargo test
  ```
  ```bash
  cd local_file_disclosure_server-fix && cargo test
  ```
- Expected results:
  - Vulnerable: test shows that `sensitive.txt` is reachable via `/public`.
  - Fixed: tests confirm the file is not reachable (404/403/400) and traversal is blocked.

## Notes
- The file `sensitive.txt` at the project root represents data that should never be served by static hosting.
- The fixed server maps `/public` to `./static` only; the vulnerable server maps `/public` to the entire project directory (`.`).