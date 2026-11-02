# Checkmarx One Integration

The workflow [`.github/workflows/checkmarx.yml`](../.github/workflows/checkmarx.yml) uses the official [`checkmarx/ast-github-action`](https://github.com/Checkmarx/ast-github-action). Nothing tenant-specific is hard-coded.

## Required configuration

Set these in **Settings → Secrets and variables → Actions** (repository or organization level). Values are provided by your Checkmarx One administrator / ASoD team — do not guess them.

| Name | Type | Description |
|---|---|---|
| `CX_CLIENT_ID` | Secret | OAuth client ID for this integration |
| `CX_CLIENT_SECRET` | Secret | OAuth client secret |
| `CX_BASE_URI` | Variable | Checkmarx One base URL for your tenant's region |
| `CX_TENANT` | Variable | Checkmarx One tenant name |

## Optional variables

| Name | Default | Purpose |
|---|---|---|
| `CX_PROJECT_NAME` | `owner/repo` | Project name agreed during onboarding |
| `CX_SCAN_TYPES` | `sast,sca,iac-security` | Add `scs` (and `container-security`) if licensed |
| `CX_FILE_FILTER` | `!remediation/**` | Excludes prepared fix patches from scanning |
| `CX_THRESHOLD` | *(none)* | e.g. `sast-high=1;sca-high=1` to fail the build |
| `CX_EXTRA_SCAN_PARAMS` | *(none)* | e.g. `--scs-engines secret-detection`, `--sast-preset-name "<preset>"`, `--project-groups "<group>"`, `--application-name "<app>"` |

> Validate every flag against the `cx` CLI version bundled with the pinned action, and confirm presets, groups and applications with your administrator.

## What the workflow does

1. **prepare** – checkout, Python 3.13, install dependencies, run tests.
2. **checkmarx-scan** (only when `CX_BASE_URI` is set) – runs the scan, decorates PRs, writes `cx_result.sarif`.
3. Uploads SARIF to GitHub code scanning (`security-events: write`; private repos need GitHub Advanced Security for code scanning).
4. Uploads `cx_result.*` as a build artifact and writes a job summary with the scan ID.
5. **not-configured** – prints a notice when Checkmarx is not configured, keeping the repository usable before onboarding.

Triggers: PR to `main`, push to `main`, `v*` tags, manual dispatch, weekly schedule (continuous monitoring).

## Demo tip: thresholds

Leave `CX_THRESHOLD` empty for the baseline so the scan completes and results are visible. Set it after remediation to show the pipeline acting as a **gate** that prevents re-introduction.

## Replacing with a centralized reusable workflow

Organizations usually own scanning centrally (versions, flags, thresholds, result routing). This repository is designed so the local workflow can be swapped out:

- Caller example: [`examples/call-central-security-workflow.yml`](examples/call-central-security-workflow.yml)
- Sketch of a central reusable workflow: [`examples/central-reusable-checkmarx-workflow.yml`](examples/central-reusable-checkmarx-workflow.yml)

Steps: copy the caller to `.github/workflows/security.yml`, replace `<ORG>`, `<CENTRAL_WORKFLOWS_REPO>`, `<CHECKMARX_WORKFLOW>` and `<REF>` with the real values, then delete `checkmarx.yml` to avoid duplicate scans.

## Local scanning (optional)

If the Checkmarx One CLI (`cx`) is installed and authenticated per your organization's instructions, the same scan can be launched locally, e.g.:

```bash
cx scan create --project-name "<project>" -s . --branch "$(git branch --show-current)" \
  --scan-types sast,sca,iac-security --file-filter '!remediation/**' \
  --report-format sarif --output-path . --output-name cx_result
```

IDE plugins (VS Code, JetBrains) can show the same results to developers during remediation.
