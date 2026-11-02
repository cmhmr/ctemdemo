"""CTEM-IAC-01 (CWE-250, runs as root) and CTEM-IAC-02 (missing HEALTHCHECK)."""

import re
from pathlib import Path

import pytest

DOCKERFILE = (Path(__file__).resolve().parents[2] / "Dockerfile").read_text()


@pytest.mark.xfail(strict=True, reason="CTEM-IAC-01 open in v0.1-demo-vulnerable")
def test_container_runs_as_non_root_user():
    users = re.findall(r"^USER\s+(\S+)", DOCKERFILE, re.MULTILINE)
    assert users and users[-1] not in {"root", "0", "0:0"}


@pytest.mark.xfail(strict=True, reason="CTEM-IAC-02 open in v0.1-demo-vulnerable")
def test_container_defines_healthcheck():
    assert re.search(r"^HEALTHCHECK\s", DOCKERFILE, re.MULTILINE)
