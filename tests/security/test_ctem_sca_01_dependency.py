"""CTEM-SCA-01 | Known-vulnerable third-party dependency (requests)."""

import re
from pathlib import Path

import pytest

VULNERABLE = pytest.mark.xfail(strict=True, reason="CTEM-SCA-01 open in v0.1-demo-vulnerable")
MANIFEST = Path(__file__).resolve().parents[2] / "requirements-demo-sca.txt"
# Minimum version without the advisories listed in requirements-demo-sca.txt.
MINIMUM_SAFE = (2, 33, 0)


@VULNERABLE
def test_requests_pin_is_not_below_patched_version():
    match = re.search(r"^requests==(\d+)\.(\d+)\.(\d+)", MANIFEST.read_text(), re.MULTILINE)
    assert match, "requests pin not found"
    assert tuple(int(x) for x in match.groups()) >= MINIMUM_SAFE
