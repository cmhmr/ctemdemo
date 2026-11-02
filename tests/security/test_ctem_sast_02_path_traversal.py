"""CTEM-SAST-02 | CWE-22 | Path traversal in datasheet viewer."""

import pytest

VULNERABLE = pytest.mark.xfail(strict=True, reason="CTEM-SAST-02 open in v0.1-demo-vulnerable")


@VULNERABLE
def test_datasheet_cannot_read_application_source(client):
    # Benign lab-only probe: attempts to read the app's own config module.
    resp = client.get("/products/1/datasheet", query_string={"file": "../../config.py"})
    assert "def load_config" not in resp.get_data(as_text=True)
