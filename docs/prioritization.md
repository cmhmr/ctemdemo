# Contextual Prioritization (Illustrative Model)

> This is a **teaching model**, not a Checkmarx feature and not real scan output. The "expected" column describes the pattern's nature; actual scanner severity must be read from your Checkmarx One results.

## Why context matters

Scanner severity answers *"how bad is this class of weakness?"*. CTEM prioritization answers *"how much risk does this exposure create for **this** business, **now**?"*.

## Factors

| Factor | Source | Values (example weight) |
|---|---|---|
| Scanner severity | Checkmarx One | Critical 4 · High 3 · Medium 2 · Low 1 |
| Exposure / reachability | Route auth, network exposure (`ctem-scope.yml`), SCA reachability | Unauthenticated 3 · Authenticated 2 · Not reachable / build-only 1 |
| Data sensitivity | Data classification | Restricted 3 · Confidential/credentials 2 · Internal 1 |
| Validation status | Regression test / manual verification / triage | Validated 1.5× · Unvalidated 1× · Not exploitable 0.2× |
| Asset criticality | ASoD / CMDB | Critical 1.5× · High 1.25× · Medium 1× · Low 0.75× |

`Priority score = severity × exposure × data × validation × criticality`

## Worked example for CTEM Demo Store

Context from [`ctem-scope.yml`](../ctem-scope.yml): internal exposure, stores credentials, medium criticality. Severities below are **assumptions for the exercise** — replace with real values during the demo.

| Scenario | Assumed severity | Exposure | Data | Validation | Score | Rank |
|---|---|---|---|---|---|---|
| CTEM-SAST-01 SQL injection | High (3) | Unauth (3) | Credentials (2) | Validated (1.5) | 27 | 1 |
| CTEM-SECRET-01 Hard-coded credential | High (3) | Repo access (2) | Credentials (2) | Validated (1.5) | 18 | 2 (see note) |
| CTEM-SAST-02 Path traversal | High (3) | Unauth (3) | Internal (1) | Validated (1.5) | 13.5 | 3 |
| CTEM-SAST-03 Weak hash | Medium (2) | Chained via SAST-01 (2) | Credentials (2) | Validated (1.5) | 12 | 4 |
| CTEM-SAST-05 Input validation | Medium (2) | Auth (2) | Internal (1) | Validated (1.5) | 6 | 5 |
| CTEM-SAST-04 Password in logs | Medium (2) | Log access (1) | Credentials (2) | Validated (1.5) | 6 | 5 |
| CTEM-IAC-01 Root container | Medium (2) | Amplifier (1) | Internal (1) | Validated (1.5) | 3 | 7 |
| CTEM-IAC-02 No HEALTHCHECK | Low (1) | Amplifier (1) | Internal (1) | Validated (1.5) | 1.5 | 8 |
| CTEM-SCA-01 requests 2.31.0 | Medium (2) | Not imported (1) | Internal (1) | Not reachable (0.2) | 0.4 | 9 |

**Discussion notes**

- **SECRET-01:** for a *real* credential this is an immediate incident (rotate first, then fix code) regardless of score. Here it is fake, so it is scheduled with the code fixes — say this explicitly.
- **SAST-01 + SAST-03 chain:** fixing SAST-01 also reduces the effective risk of SAST-03; both are still fixed.
- **SCA-01:** high CVE count does not equal high risk when the vulnerable code is not reachable. Still upgrade (cheap, prevents future reachability).
- Change one context value (e.g. `exposure: internet-facing`) and re-rank to show how CTEM reacts to business context.

## Disposition outcomes

| Disposition | When | Record in |
|---|---|---|
| Fix now | Top-ranked, within SLA | Issue + PR |
| Fix scheduled | Lower rank, SLA allows | Backlog with due date |
| Risk accepted | Business decision, time-boxed | Checkmarx triage state + ASoD exception record |
| False positive / Not exploitable | Validation shows no real path | Checkmarx triage state + justification |
