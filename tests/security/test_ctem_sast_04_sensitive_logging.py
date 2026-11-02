"""CTEM-SAST-04 | CWE-532 | Sensitive information written to logs."""

import logging

import pytest

from tests.conftest import login

VULNERABLE = pytest.mark.xfail(strict=True, reason="CTEM-SAST-04 open in v0.1-demo-vulnerable")


@VULNERABLE
def test_login_does_not_log_password(client, caplog):
    caplog.set_level(logging.DEBUG)
    login(client, password="Distinctive-Pa55word")
    assert "Distinctive-Pa55word" not in caplog.text
