# Security regression tests

One file per CTEM scenario. Each test asserts the **secure** behavior.

In the vulnerable state (`v0.1-demo-vulnerable`) each test is marked
`@pytest.mark.xfail(strict=True)`: the suite stays green, and the report shows
which exposures are still open (`XFAIL`).

When a scenario is remediated, its test starts passing. Because the marker is
`strict`, an unexpected pass (`XPASS`) fails the build until the marker is
removed - the remediation patch removes it, turning the test into a permanent
regression guard. This is the "validation" and "continuous monitoring" evidence
in the CTEM loop, complementary to the Checkmarx re-scan.
