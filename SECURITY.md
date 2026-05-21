# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

To report a security vulnerability, please **do not** open a public GitHub issue.
Instead, email the project maintainer directly at the contact listed in the repository.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigations

You will receive a response within 7 business days.

## Scope

This project is a research and educational tool. The following are **in scope**:

- Dependency vulnerabilities (e.g., a CVE in a Python package we depend on)
- Code injection risks in SMILES parsing or file upload handling
- Cross-site scripting (XSS) risks in the Streamlit interface
- Unintended remote code execution paths

The following are **out of scope**:

- Issues with the accuracy or completeness of scientific predictions
  (those should be filed as standard GitHub issues)
- Social engineering attacks

## Important notes for public demo deployments

- This app is intended for educational and research use only.
- **Do not upload protected health information (PHI), confidential patient data,
  proprietary compound structures under NDA, or personally identifiable
  information (PII) to any public deployment of this app.**
- Streamlit Community Cloud and similar platforms may log session data.
  Review the platform's privacy policy before uploading sensitive structures.
- Model artifacts in `models/` were trained on the public TDC Caco2_Wang
  benchmark and do not contain proprietary data.

## Disclaimer

This software is provided "as is" without warranty of any kind. It is not
intended for clinical, regulatory, safety, or medical decision-making.
See LICENSE for the full disclaimer.
