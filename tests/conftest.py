import re

import pytest

from ctem_demo import create_app

DEMO_PASSWORD = "test-password"


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("CTEM_DEMO_PASSWORD", DEMO_PASSWORD)
    monkeypatch.delenv("CTEM_INVENTORY_API_KEY", raising=False)
    application = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db")})
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


def csrf_token(client, path="/login"):
    page = client.get(path).get_data(as_text=True)
    match = re.search(r'name="_csrf" value="([^"]+)"', page)
    assert match, f"no CSRF token found on {path}"
    return match.group(1)


def login(client, username="analyst", password=DEMO_PASSWORD):
    token = csrf_token(client)
    return client.post(
        "/login",
        data={"username": username, "password": password, "_csrf": token},
        follow_redirects=False,
    )


@pytest.fixture
def logged_in(client):
    assert login(client).status_code == 302
    return client
