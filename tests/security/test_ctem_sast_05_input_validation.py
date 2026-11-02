"""CTEM-SAST-05 | CWE-20 / CWE-1284 | Insufficient input validation on reorder quantity."""

import pytest

from tests.conftest import csrf_token

VULNERABLE = pytest.mark.xfail(strict=True, reason="CTEM-SAST-05 open in v0.1-demo-vulnerable")


@VULNERABLE
@pytest.mark.parametrize("quantity", ["-1000", "0", "999999", "abc", "1.5"])
def test_reorder_rejects_invalid_quantity(logged_in, quantity):
    token = csrf_token(logged_in, "/products/1")
    resp = logged_in.post("/products/1/reorder", data={"quantity": quantity, "_csrf": token})
    assert resp.status_code == 400
    assert '<dd id="stock">42</dd>' in logged_in.get("/products/1").get_data(as_text=True)
