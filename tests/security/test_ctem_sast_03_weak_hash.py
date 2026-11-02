"""CTEM-SAST-03 | CWE-327 / CWE-916 | Weak password hashing."""

import hashlib

import pytest

from ctem_demo.passwords import hash_password, verify_password

VULNERABLE = pytest.mark.xfail(strict=True, reason="CTEM-SAST-03 open in v0.1-demo-vulnerable")


@VULNERABLE
def test_password_hash_is_salted_and_not_md5():
    first, second = hash_password("s3cret"), hash_password("s3cret")
    assert first != second, "hashes must be salted"
    assert first != hashlib.md5(b"s3cret").hexdigest()
    assert verify_password("s3cret", first)
    assert not verify_password("wrong", first)
