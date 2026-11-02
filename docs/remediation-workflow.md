# Remediation & Git Workflow

The vulnerable and remediated states are **the same application at two points in history**, not two apps.

```text
main ──●───────────────●──────●──────●──────●───── ...
       │               │      │      │      │
 v0.1-demo-vulnerable  fix/   fix/   fix/   v0.2-demo-remediated
       │               SAST-01 SECRET-01 ...
       └─ Checkmarx scan #1 (baseline)          └─ Checkmarx scan #N (re-scan)
```

## One-time setup (publish as its own repository)

This folder is designed to be the **root** of its own GitHub repository (GitHub Actions only runs workflows from the repository root `.github/workflows/`).

```bash
# from this folder
git init -b main
git add .
git commit -m "CTEM Demo Store: vulnerable baseline"
git tag -a v0.1-demo-vulnerable -m "CTEM demo: vulnerable baseline"
git remote add origin <your-repo-url>
git push -u origin main --tags
```

Configure Checkmarx secrets/variables first (see [`checkmarx-integration.md`](checkmarx-integration.md)) so the baseline scan runs on the first push and on the tag.

## Remediation loop (per prioritized finding)

```bash
git switch -c fix/CTEM-SAST-01-sql-injection
scripts/apply-remediation.sh CTEM-SAST-01        # or implement the fix live
python -m pytest -ra                              # XFAIL -> PASS for this scenario
git commit -am "fix(CTEM-SAST-01): parameterize product search query (CWE-89)"
git push -u origin HEAD
# open a PR -> CI + Checkmarx PR scan; reviewer sees the finding resolved
```

Merge, then repeat in priority order (see [`prioritization.md`](prioritization.md)). Suggested order:

1. `CTEM-SAST-01` SQL injection
2. `CTEM-SECRET-01` hard-coded credential (+ rotation step in the PR description)
3. `CTEM-SAST-02` path traversal
4. `CTEM-SAST-03` weak password hash
5. `CTEM-SAST-05` input validation
6. `CTEM-SAST-04` sensitive logging
7. `CTEM-IAC-01-02` container hardening
8. `CTEM-SCA-01` dependency upgrade

Each patch is independent: any subset, any order.

```bash
scripts/apply-remediation.sh --list             # available patches
scripts/apply-remediation.sh --check --all      # dry-run all
scripts/apply-remediation.sh --all              # fast path (e.g. rehearsal)
```

## Close the release

```bash
# after all fixes are merged to main
export CTEM_APP_VERSION=0.2.0-demo-remediated   # or update the default in ctem_demo/config.py
git tag -a v0.2-demo-remediated -m "CTEM demo: remediated"
git push origin v0.2-demo-remediated
```

Compare the Checkmarx One scans of the two tags to show risk reduction. **Use only real scan output.**

## Resetting for the next demo

```bash
git switch main
git reset --hard v0.1-demo-vulnerable   # local rehearsal only
```

For a shared repository prefer a dedicated `demo/<date>` branch from `v0.1-demo-vulnerable` instead of rewriting `main`.

## Commit message convention

```
fix(<SCENARIO-ID>): <what changed> (<CWE>)

Finding: <Checkmarx result link or ID>
Validation: tests/security/<test file> now passes
Disposition: fixed
```

## About Git history and secrets

Removing `CTEM-SECRET-01` from the code does **not** remove it from history. For real credentials: rotate/revoke first, then decide on history rewriting per your policy. The demo value is fake, so no rotation is needed — but narrate the step.
