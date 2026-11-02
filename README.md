# CTEM Demo Store

**A small, deployable Python application that demonstrates how Checkmarx One participates in a Continuous Threat Exposure Management (CTEM) lifecycle.**

> ⚠️ **Training / lab use only.** This application intentionally contains insecure code and configuration patterns for security-scanning demonstrations. All examples are local, deterministic and non-destructive. The embedded credential-like value is **fake**. Never deploy this outside an isolated lab. See [SECURITY.md](SECURITY.md).

```text
Application → GitHub repository → GitHub Actions → Checkmarx One scanning → Security findings
   → Contextual prioritization → Developer remediation → Re-scan → Risk reduction
```

## CTEM stages in this repository

| CTEM stage | What to show | Where |
|---|---|---|
| 1. Scoping | Business context, owner, exposure, in/out of scope | [`ctem-scope.yml`](ctem-scope.yml), [`docs/asod-integration.md`](docs/asod-integration.md) |
| 2. Discovery | Checkmarx One SAST / SCA / IaC / Secrets in CI | [`.github/workflows/checkmarx.yml`](.github/workflows/checkmarx.yml) |
| 3. Prioritization | Severity × exposure × data × validation × criticality | [`docs/prioritization.md`](docs/prioritization.md) |
| 4. Validation | Data-flow evidence + benign local regression tests | [`tests/security/`](tests/security/) |
| 5. Mobilization | Owner, issue, PR, independent fix patches | [`remediation/patches/`](remediation/patches/), [`docs/remediation-workflow.md`](docs/remediation-workflow.md) |
| 6. Re-scan / Monitoring | PR/main/tag/weekly scans, strict regression tests | [`docs/ctem-lifecycle.md`](docs/ctem-lifecycle.md) |

Full narrative: [`docs/ctem-lifecycle.md`](docs/ctem-lifecycle.md) · Presenter script: [`docs/demo-runbook.md`](docs/demo-runbook.md)

## The application

A simple internal inventory portal (Flask + Jinja + SQLite):

| Route | Description | Auth |
|---|---|---|
| `/` | Home with inventory stats | – |
| `/products` | Product listing | – |
| `/products/search?q=` | Product search | – |
| `/products/<id>` | Product details (+ reorder form when signed in) | – |
| `/products/<id>/datasheet?file=` | Plain-text datasheet viewer | – |
| `/products/<id>/reorder` (POST) | Reorder stock | user |
| `/login`, `/logout` | Session login | – |
| `/profile` | User profile | user |
| `/admin/status` | Admin status page | admin |
| `/health` | JSON health check | – |

Lab accounts: `analyst` (user) and `admin` (admin). Password: value of `CTEM_DEMO_PASSWORD` (default `ctem-demo`). The database is rebuilt on every start, so each demo begins from the same state.

## Quick start

### Local (Python 3.13)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                      # http://127.0.0.1:8080
```

### Docker

```bash
docker build -t ctem-demo .
docker run -p 8080:8080 ctem-demo
# or: docker compose up --build    (binds to 127.0.0.1:8080)
```

### Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -ra
```

In the vulnerable state you will see functional tests **pass** and security regression tests reported as **XFAIL** (open exposures). After all fixes: everything passes.

## Configuration (environment variables)

No real secrets are needed. See [`.env.example`](.env.example).

| Variable | Default | Purpose |
|---|---|---|
| `CTEM_HOST` / `CTEM_PORT` | `127.0.0.1` / `8080` (`0.0.0.0` in Docker) | Bind address |
| `CTEM_SECRET_KEY` | random per process | Flask session signing key |
| `CTEM_DEMO_PASSWORD` | `ctem-demo` | Password for the seeded lab accounts |
| `CTEM_DATABASE_PATH` | `instance/ctem_demo.db` | SQLite file (recreated at startup) |
| `CTEM_APP_ENV` / `CTEM_APP_VERSION` | `lab` / `0.1.0-demo-vulnerable` | Displayed on status page and `/health` |
| `CTEM_LOG_LEVEL` | `INFO` | Logging level |
| `CTEM_INVENTORY_API_KEY` | *(unset)* | Used once CTEM-SECRET-01 is remediated (any dummy value) |
| `CTEM_MAX_REORDER_QUANTITY` | `500` | Used once CTEM-SAST-05 is remediated |
| `CTEM_SECURE_COOKIES` | `false` | Set `true` behind HTTPS |

## Security scenarios

| ID | Type | CWE | File |
|---|---|---|---|
| CTEM-SAST-01 | SQL injection | CWE-89 | `ctem_demo/catalog.py` |
| CTEM-SAST-02 | Path traversal | CWE-22 | `ctem_demo/datasheets.py` |
| CTEM-SAST-03 | Weak password hash (MD5) | CWE-327 / CWE-916 | `ctem_demo/passwords.py` |
| CTEM-SAST-04 | Password in logs | CWE-532 | `ctem_demo/auth.py` |
| CTEM-SAST-05 | Insufficient input validation | CWE-20 / CWE-1284 | `ctem_demo/catalog.py` |
| CTEM-SECRET-01 | Hard-coded **fake** credential | CWE-798 | `ctem_demo/integrations.py` |
| CTEM-SCA-01 | Vulnerable dependency (isolated) | CWE-1395 | `requirements-demo-sca.txt` |
| CTEM-IAC-01 | Container runs as root | CWE-250 | `Dockerfile` |
| CTEM-IAC-02 | No container HEALTHCHECK | – | `Dockerfile` |

Details (vulnerable behavior, impact, secure implementation, CTEM relevance): [`docs/security-scenarios.md`](docs/security-scenarios.md).

This repository does **not** contain or predict Checkmarx scan results. Always present real output from your tenant.

## Vulnerable → remediated

Both states are the same codebase at different points in Git history:

```text
v0.1-demo-vulnerable ──► findings ──► prioritization ──► fix commits (one per scenario) ──► v0.2-demo-remediated
```

```bash
scripts/apply-remediation.sh --list
scripts/apply-remediation.sh CTEM-SAST-01      # apply one independent fix
```

See [`docs/remediation-workflow.md`](docs/remediation-workflow.md).

## Checkmarx One / ASoD

- Workflow and required secrets/variables: [`docs/checkmarx-integration.md`](docs/checkmarx-integration.md)
- Centralized reusable workflow example: [`docs/examples/call-central-security-workflow.yml`](docs/examples/call-central-security-workflow.yml)
- ASoD integration points (no invented APIs): [`docs/asod-integration.md`](docs/asod-integration.md)

> This folder is meant to be the **root of its own GitHub repository**; GitHub Actions only runs workflows from the root `.github/workflows/` directory.

## Repository layout

```text
app.py                         entry point (python app.py)
ctem_demo/                     Flask application package
  catalog.py datasheets.py auth.py admin.py passwords.py integrations.py db.py config.py
  templates/ static/ data/datasheets/
tests/                         functional tests
tests/security/                one regression test per scenario (strict xfail while open)
remediation/patches/           one independent fix per scenario
scripts/apply-remediation.sh   demo helper
ctem-scope.yml                 illustrative CTEM scoping record
requirements.txt               runtime deps (+ -r requirements-demo-sca.txt)
requirements-demo-sca.txt      isolated SCA demonstration dependencies
requirements-dev.txt           test deps
Dockerfile docker-compose.yml  container (intentional IaC findings)
.github/workflows/             ci.yml, checkmarx.yml
docs/                          lifecycle, scenarios, prioritization, remediation, Checkmarx, ASoD, runbook
```
