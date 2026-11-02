# Security Scenarios Catalog

> **Training / lab use only.** Every scenario below is intentional, local, deterministic and non-destructive. None of them reaches external systems. Do not deploy this application outside an isolated lab.

Each scenario is:

- tagged in the code with a `CTEM-<CATEGORY>-<NN>` comment block,
- covered by a regression test in [`tests/security/`](../tests/security/) (strict `xfail` while open),
- fixed by exactly one patch in [`remediation/patches/`](../remediation/patches/) that touches only that scenario's files.

> **Important:** This catalog describes what each pattern *is*. It does **not** predict or fabricate Checkmarx results. Engines, presets, queries and advisory feeds change over time. Always demo using real scan output, and use this table to explain it.

## Summary

| ID | Category | CWE | Location | Fix patch |
|---|---|---|---|---|
| CTEM-SAST-01 | SAST – SQL injection | CWE-89 | [`ctem_demo/catalog.py`](../ctem_demo/catalog.py) `search()` | `CTEM-SAST-01-sql-injection.patch` |
| CTEM-SAST-02 | SAST – Path traversal | CWE-22 | [`ctem_demo/datasheets.py`](../ctem_demo/datasheets.py) `view_datasheet()` | `CTEM-SAST-02-path-traversal.patch` |
| CTEM-SAST-03 | SAST – Weak crypto | CWE-327, CWE-916 | [`ctem_demo/passwords.py`](../ctem_demo/passwords.py) `hash_password()` | `CTEM-SAST-03-weak-password-hash.patch` |
| CTEM-SAST-04 | SAST – Sensitive logging | CWE-532 | [`ctem_demo/auth.py`](../ctem_demo/auth.py) `login()` | `CTEM-SAST-04-sensitive-logging.patch` |
| CTEM-SAST-05 | SAST – Input validation | CWE-20, CWE-1284 | [`ctem_demo/catalog.py`](../ctem_demo/catalog.py) `reorder()` | `CTEM-SAST-05-input-validation.patch` |
| CTEM-SECRET-01 | Secrets | CWE-798 | [`ctem_demo/integrations.py`](../ctem_demo/integrations.py) | `CTEM-SECRET-01-hardcoded-credential.patch` |
| CTEM-SCA-01 | SCA – Vulnerable dependency | CWE-1395 | [`requirements-demo-sca.txt`](../requirements-demo-sca.txt) | `CTEM-SCA-01-vulnerable-dependency.patch` |
| CTEM-IAC-01 | Container – runs as root | CWE-250 | [`Dockerfile`](../Dockerfile) | `CTEM-IAC-01-02-container-hardening.patch` |
| CTEM-IAC-02 | Container – no HEALTHCHECK | CWE-1188 (insecure default; availability) | [`Dockerfile`](../Dockerfile) | `CTEM-IAC-01-02-container-hardening.patch` |

---

## CTEM-SAST-01 — SQL injection in product search

| | |
|---|---|
| **CWE** | CWE-89: Improper Neutralization of Special Elements used in an SQL Command |
| **File** | `ctem_demo/catalog.py` → `search()` |
| **Vulnerable behavior** | The `q` query parameter is interpolated into the SQL string with an f-string and executed. A quote changes the query structure; a `UNION SELECT` can read other tables (the demo `users` table, including password hashes). |
| **Business / security impact** | Unauthenticated read access to any data in the database; credential hashes exposed (which compounds with SAST-03). Typical root cause of data breaches. |
| **Secure implementation** | Parameterized query: `execute("… WHERE name LIKE ? OR category LIKE ?", (pattern, pattern))`. Bound parameters are never parsed as SQL. Optionally cap input length. |
| **CTEM relevance** | High-impact, reachable from an unauthenticated route, and *validatable* (the regression test is a benign local probe). Usually ranks first after contextual prioritization. |

## CTEM-SAST-02 — Path traversal in datasheet viewer

| | |
|---|---|
| **CWE** | CWE-22: Improper Limitation of a Pathname to a Restricted Directory |
| **File** | `ctem_demo/datasheets.py` → `view_datasheet()` |
| **Vulnerable behavior** | The `file` parameter is joined to the datasheet directory with `os.path.join` and opened. `../` sequences (or an absolute path) escape the directory and read arbitrary files the process can access (e.g. application source/config). |
| **Business / security impact** | Disclosure of source code, configuration or secrets on disk; aids further attacks. |
| **Secure implementation** | Don't accept paths from users: use the file name stored on the product record, `resolve()` it and verify `path.is_relative_to(base_dir)` before reading. |
| **CTEM relevance** | Unauthenticated and reachable; impact depends on what is on disk — a good example for discussing *environmental context* (container filesystem vs. shared host). |

## CTEM-SAST-03 — Weak password hashing (unsalted MD5)

| | |
|---|---|
| **CWE** | CWE-327: Use of a Broken or Risky Cryptographic Algorithm; CWE-916: Use of Password Hash With Insufficient Computational Effort |
| **File** | `ctem_demo/passwords.py` → `hash_password()` |
| **Vulnerable behavior** | Passwords are stored as unsalted MD5 hex digests. Identical passwords produce identical hashes; MD5 is extremely fast to brute-force. |
| **Business / security impact** | Any database leak (e.g. via SAST-01) turns into cleartext credentials quickly; credential reuse extends the blast radius. |
| **Secure implementation** | Salted adaptive KDF: `werkzeug.security.generate_password_hash(password, method="scrypt")` and `check_password_hash()`. Plan a rehash-on-login migration for existing users in real systems. |
| **CTEM relevance** | Demonstrates *exposure chaining*: medium on its own, higher when combined with SAST-01. |

## CTEM-SAST-04 — Plaintext password written to logs

| | |
|---|---|
| **CWE** | CWE-532: Insertion of Sensitive Information into Log File |
| **File** | `ctem_demo/auth.py` → `login()` |
| **Vulnerable behavior** | Each login attempt logs `username=… password=…` in cleartext. |
| **Business / security impact** | Anyone with log access (operators, SIEM, log-shipping vendors, backups) can harvest credentials. Often a compliance finding (PCI DSS, SOC 2). |
| **Secure implementation** | Log the event and outcome only (`Login succeeded/failed username=…`), strip CR/LF from user-controlled values (CWE-117), never log secrets or tokens. |
| **CTEM relevance** | Not externally exploitable by itself — good example of a finding that is *real* but prioritized lower than reachable injection flaws. |

## CTEM-SAST-05 — Insufficient validation of reorder quantity

| | |
|---|---|
| **CWE** | CWE-20: Improper Input Validation; CWE-1284: Improper Validation of Specified Quantity in Input |
| **File** | `ctem_demo/catalog.py` → `reorder()` |
| **Vulnerable behavior** | `int(request.form["quantity"])` is trusted: negative or huge values corrupt stock; non-numeric values raise an unhandled exception (HTTP 500). |
| **Business / security impact** | Data integrity issue (inventory manipulation) by any authenticated user; error noise / availability. |
| **Secure implementation** | Server-side type and range validation (`isdecimal()`, `1 ≤ n ≤ MAX_REORDER_QUANTITY`), return HTTP 400 with a user-friendly message. The HTML `min`/`max` attributes are UX only, not a control. |
| **CTEM relevance** | Requires authentication → lower exposure. Useful for explaining why "authenticated-only" changes priority. Scanners may report this under different query names (or not at all) — a good triage/validation discussion point. |

## CTEM-SECRET-01 — Hard-coded (fake) credential

| | |
|---|---|
| **CWE** | CWE-798: Use of Hard-coded Credentials |
| **File** | `ctem_demo/integrations.py` → `INVENTORY_API_KEY` |
| **Vulnerable behavior** | An API-key-like string is committed in source. **The value is FAKE and non-functional** (prefix `ctemdemo_FAKE_` + random hex generated for this POC). It does not match any vendor key format and is never sent anywhere. |
| **Business / security impact** | In real life: anyone with repository access (or a leaked clone/fork) obtains the credential; it persists in Git history even after deletion. |
| **Secure implementation** | Read from the environment (`CTEM_INVENTORY_API_KEY`) injected by a secrets manager / CI secret. **Rotate** any credential ever committed; consider history rewrite per policy; enable push protection. |
| **CTEM relevance** | Shows that remediation ≠ code change only: mobilization involves the credential owner (rotation). Secret detection may require enabling `scs` / secret detection in your tenant. |

> The patch file `remediation/patches/CTEM-SECRET-01-hardcoded-credential.patch` necessarily contains the fake value in its removed line. The Checkmarx workflow excludes `remediation/**` by default (`CX_FILE_FILTER`) so it does not reappear as a finding after remediation. It will still exist in Git history — which is exactly the real-world lesson.

## CTEM-SCA-01 — Known-vulnerable third-party dependency

| | |
|---|---|
| **CWE** | CWE-1395: Dependency on Vulnerable Third-Party Component |
| **File** | `requirements-demo-sca.txt` (included from `requirements.txt` via `-r`) |
| **Vulnerable behavior** | `requests==2.31.0` is pinned. Published advisories (verified in OSV on 2026-11-02): GHSA-9wx4-h78v-vm56 / CVE-2024-35195 (fixed 2.32.0), GHSA-9hjg-9r4m-mvj7 / CVE-2024-47081 (fixed 2.32.4), GHSA-gc5v-m9x4-r6x2 / CVE-2026-25645 (fixed 2.33.0). The app does **not** import `requests` at runtime. |
| **Business / security impact** | Inherited vulnerabilities from the supply chain; exploitability depends on whether vulnerable code paths are used. |
| **Secure implementation** | Upgrade to a version without known advisories (patch uses `2.34.2`), keep a lockfile, enable automated dependency updates. |
| **CTEM relevance** | Ideal to discuss **reachability / exploitability**: the package is installed but unused, so contextual priority is lower than CVSS alone suggests. Also shows continuous monitoring: new CVEs appear without code changes (scheduled re-scan). |

**Why a separate file?** Advisory data and scanner behavior evolve. Keeping demo dependencies isolated means you can update them without touching the application. **Review this file before every demo.** If your SCA tool does not follow `-r` includes, add the pin directly to `requirements.txt`.

## CTEM-IAC-01 / CTEM-IAC-02 — Container hardening

| | |
|---|---|
| **CWE** | IAC-01: CWE-250 Execution with Unnecessary Privileges. IAC-02: missing health monitoring (insecure default configuration). |
| **File** | `Dockerfile` |
| **Vulnerable behavior** | No `USER` instruction, so the process runs as root inside the container. No `HEALTHCHECK`, so the orchestrator cannot detect an unhealthy app. |
| **Business / security impact** | Any code-execution bug becomes root in the container, easing escape/lateral movement; silent failures reduce availability. |
| **Secure implementation** | Create an unprivileged user (`useradd --system`), `chown` only writable paths (`/app/instance`), `USER app`, and add a `HEALTHCHECK` calling `/health`. Also consider pinning the base image by digest and a read-only root filesystem at runtime. |
| **CTEM relevance** | Amplifiers: they don't create an entry point but increase impact of other exposures. Good example of "fix cheaply, reduce blast radius". |

## Expected additional observations

Real scanners may also report items that are **not** part of the planned catalog, for example:

- the lab default password fallback `ctem-demo` in `ctem_demo/db.py` (`CTEM_DEMO_PASSWORD`),
- the benign probe strings in `tests/security/`,
- the Flask development server used by `python app.py`,
- base-image OS package CVEs if container scanning is enabled.

Treat them as part of the demo: triage, decide (fix / accept / false positive / not applicable) and record the disposition. That *is* CTEM prioritization.
