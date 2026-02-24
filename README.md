# Practical_3_Codes

This repository contains example vulnerable code and fixed versions used for Practical 3 testing exercises.

Overview of top-level folders

- **Access_Control_Vuln**: examples demonstrating access control vulnerabilities (vulnerable and fixed versions, plus supporting files).
- **Audit_Logging_Vuln**: examples showing logging issues (includes vulnerable and fixed scripts).
- **Auth_Bypass_Vuln**: authentication bypass examples in PHP (vulnerable and fixed files).
- **CSRF**: Cross-Site Request Forgery examples and test pages.
- **File_Upload_Vuln**: insecure and secure file upload examples, plus sample payloads and upload directories.
- **Input_ValidationVuln**: input validation failure and fixed examples.
- **Local_File_Disclosure**: examples demonstrating local file disclosure (vulnerable and fixed server projects).
- **Session_Mgmt_Vuln**: session management insecure and secure examples and helpers.
- **tmp**: scratch or output files used during exercises (e.g., hacked.txt).

How to use this repository

- Each folder includes its own `README.md` with specific instructions for running and testing the vulnerability in that folder. Start by opening the folder README to see prerequisites and test steps.
- Some folders include dependency manifests such as `package.json`, `requirements.txt`, or Rust `Cargo.toml`—follow the per-folder README for installation steps.
- Where both vulnerable and fixed versions exist, the filenames typically use `_vuln` and `_fix` suffixes to distinguish them.

If you need help running any of the examples, mention the folder name and create an issue in the repository.