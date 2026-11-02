"""CTEM-SECRET-01 | CWE-798 | Hard-coded (fake) credential in source code."""

from pathlib import Path

import pytest

from ctem_demo import integrations

VULNERABLE = pytest.mark.xfail(strict=True, reason="CTEM-SECRET-01 open in v0.1-demo-vulnerable")


@VULNERABLE
def test_api_key_comes_from_environment(monkeypatch):
    monkeypatch.delenv("CTEM_INVENTORY_API_KEY", raising=False)
    assert integrations.get_inventory_api_key() is None
    monkeypatch.setenv("CTEM_INVENTORY_API_KEY", "dummy-value")
    assert integrations.get_inventory_api_key() == "dummy-value"


@VULNERABLE
def test_no_credential_literal_in_source():
    source = Path(integrations.__file__).read_text(encoding="utf-8")
    assert "ctemdemo_FAKE_" not in source
