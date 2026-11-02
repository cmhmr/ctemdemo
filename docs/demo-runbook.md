# Live Demo Runbook (~30–40 min)

## Before the session

- [ ] Repository published, tag `v0.1-demo-vulnerable` exists, baseline Checkmarx scan **completed** (scans take time — don't run the first one live).
- [ ] Re-checked [`requirements-demo-sca.txt`](../requirements-demo-sca.txt) against current advisories.
- [ ] App running locally or in Docker; browser tabs: app, GitHub Actions, Checkmarx One project, GitHub code scanning.
- [ ] Rehearsed `scripts/apply-remediation.sh` on a scratch branch.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py                      # http://127.0.0.1:8080  (analyst / admin, password: ctem-demo)
# or
docker build -t ctem-demo . && docker run --rm -p 8080:8080 ctem-demo
```

## 1. Scoping (3 min)

- Show the app: home, products, search, product detail, datasheet, login, profile, admin status, `/health`.
- Open [`ctem-scope.yml`](../ctem-scope.yml): owner, exposure, data classification, criticality, in/out of scope.
- Message: *"CTEM starts with business context, not with a scanner."*

## 2. Discovery (7 min)

- Show [`checkmarx.yml`](../.github/workflows/checkmarx.yml): triggers, secrets/variables, no hard-coded tenant data.
- Show the completed baseline scan in Checkmarx One: SAST, SCA, IaC (and secrets if enabled).
- Open one SAST result's data-flow (e.g. search `q` → `execute`).

## 3. Prioritization (7 min)

- Walk through [`prioritization.md`](prioritization.md) with **real** severities from the scan.
- Contrast: SCA finding with several CVEs but unused package vs. one reachable SQL injection.
- Optional: change `exposure` to `internet-facing` and re-rank.

## 4. Validation (5 min)

```bash
python -m pytest -ra tests/security    # every open exposure shows as XFAIL
```

- Explain: tests assert *secure* behavior; strict `xfail` = known open exposure.
- Optionally reproduce SAST-01 locally in the browser (lab only): search for
  `zz' UNION SELECT id, username, password_hash, role, 0 FROM users --`
  and show the demo users' hashes in the result table. Tie to SAST-03 (MD5).

## 5. Mobilization / Remediation (8 min)

```bash
git switch -c fix/CTEM-SAST-01-sql-injection
git diff --stat; scripts/apply-remediation.sh CTEM-SAST-01; git diff
python -m pytest -ra                   # SAST-01 tests now PASS
git commit -am "fix(CTEM-SAST-01): parameterize product search query (CWE-89)"
git push -u origin HEAD                # open PR
```

- Show the PR: CI green, Checkmarx PR scan / decoration.
- Mention ownership routing and SLA (see [`asod-integration.md`](asod-integration.md)).

## 6. Re-scan / Continuous monitoring (5 min)

- After merge (or using pre-prepared `v0.2-demo-remediated`): compare scans of both tags in Checkmarx One.
- Show weekly schedule trigger: new CVEs appear without code changes.
- Optionally set `CX_THRESHOLD` to show the gate preventing regressions.

## Close

*"Checkmarx provides discovery and validation evidence; context drives prioritization; the pipeline and owners drive mobilization; continuous re-scans prove risk reduction."*

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Checkmarx not configured` notice | Set `CX_BASE_URI`, `CX_TENANT`, `CX_CLIENT_ID`, `CX_CLIENT_SECRET` |
| SARIF upload fails on private repo | Code scanning requires GitHub Advanced Security; results remain in Checkmarx One and the artifact |
| Secret not reported | Enable `scs` + `--scs-engines secret-detection` (license dependent) |
| SCA finding missing | Your SCA tool may not follow `-r`; add the pin to `requirements.txt` directly |
| Patch does not apply | Branch already contains that fix, or files were edited; `git status`, then reset to the tag |
