# Security Policy

## Purpose

CTEM Demo Store is a **training and proof-of-concept** application. It **intentionally** contains insecure patterns (catalogued in [docs/security-scenarios.md](docs/security-scenarios.md)) so that security tooling and CTEM processes can be demonstrated.

## Rules of use

- Run only on a workstation or isolated lab environment. `python app.py` binds to `127.0.0.1` by default; `docker-compose.yml` publishes only on `127.0.0.1`.
- Do not expose it to the internet or to shared/production networks.
- Do not reuse any code from the vulnerable state in real applications. Use the remediated versions in `remediation/patches/` as reference.
- The credential-like value in `ctem_demo/integrations.py` is **fake and non-functional**. It does not grant access to anything.
- The demo dependency in `requirements-demo-sca.txt` is pinned to a version with published advisories on purpose; it is not imported by the app.
- Validation tests in `tests/security/` only exercise the local application and its local SQLite database/files.

## Reporting

Issues in the *intentional* scenarios are expected and should not be reported. If you find an **unintended** problem that could affect users of this POC (e.g. something that reaches outside the lab), open an issue in this repository.
