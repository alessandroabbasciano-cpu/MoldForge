# Security Policy

## Supported Versions

Currently, only the latest stable release branch is supported with security updates. Older beta versions or pre-releases are considered deprecated.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

## Reporting a Vulnerability

MOLD F.O.R.G.E. is a standalone, offline desktop application. However, security is still a priority, especially regarding local arbitrary code execution via compromised dependencies or malicious file parsing.

If you discover a vulnerability, please **do not open a public issue immediately**.

1. **Contact:** Email the address listed in the `CODE_OF_CONDUCT.md` file directly.
2. **Details:** Include the OS version, the specific MOLD F.O.R.G.E. version, and steps to reproduce the vulnerability.
3. **Response:** I am a solo developer, but I will review the report within 48 hours. If the vulnerability is verified, I will patch the codebase and push a hotfix release (e.g., `v1.0.3`) as quickly as my physical build-runners allow.

Public disclosure should only happen after a patch has been released.
