# Remediation patches

One patch per CTEM scenario. Each patch:

- changes only the files of its scenario (code + its regression test),
- removes the strict `xfail` marker so the regression test becomes a permanent guard,
- applies independently of the others, in any order.

```bash
scripts/apply-remediation.sh --list
scripts/apply-remediation.sh CTEM-SAST-01
scripts/apply-remediation.sh --check --all
```

This folder is excluded from Checkmarx scans by default (`CX_FILE_FILTER=!remediation/**`) because the diffs necessarily contain the vulnerable lines (including the fake credential) as removed context.

If you change application code, regenerate the affected patch from a clean checkout of the vulnerable baseline (`git diff > remediation/patches/<ID>.patch`) and verify with `scripts/apply-remediation.sh --check --all`.
