"""CTEM-SAST-01 | CWE-89 | SQL injection in product search."""

import pytest

VULNERABLE = pytest.mark.xfail(strict=True, reason="CTEM-SAST-01 open in v0.1-demo-vulnerable")


@VULNERABLE
def test_search_does_not_expose_user_table(client):
    # Benign lab-only probe: tries to read the local demo users table via UNION.
    probe = "zz' UNION SELECT id, username, password_hash, role, 0 FROM users --"
    resp = client.get("/products/search", query_string={"q": probe})
    body = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "riley.admin" not in body and ">admin<" not in body


@VULNERABLE
def test_search_handles_quote_characters(client):
    resp = client.get("/products/search", query_string={"q": "O'Brien"})
    assert resp.status_code == 200
