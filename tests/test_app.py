"""Functional tests: the application works as a normal inventory portal."""

from tests.conftest import csrf_token, login


def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Internal Inventory Portal" in resp.get_data(as_text=True)


def test_product_list(client):
    body = client.get("/products").get_data(as_text=True)
    assert "Edge Router ER-100" in body
    assert "USB-C Dock UD-6" in body


def test_search_returns_matches(client):
    body = client.get("/products/search?q=switch").get_data(as_text=True)
    assert "Managed Switch MS-24" in body
    assert "Edge Router ER-100" not in body


def test_search_by_category(client):
    body = client.get("/products/search?q=Networking").get_data(as_text=True)
    assert "Edge Router ER-100" in body and "Managed Switch MS-24" in body


def test_search_escapes_reflected_query(client):
    payload = "<script>alert(1)</script>"
    body = client.get("/products/search", query_string={"q": payload}).get_data(as_text=True)

    assert payload not in body
    assert body.count("&lt;script&gt;alert(1)&lt;/script&gt;") == 2


def test_product_detail_and_404(client):
    assert client.get("/products/1").status_code == 200
    assert client.get("/products/9999").status_code == 404


def test_datasheet_for_product(client):
    resp = client.get("/products/1/datasheet?file=edge-router-er100.txt")
    assert resp.status_code == 200
    assert "Product Datasheet" in resp.get_data(as_text=True)


def test_login_success_and_failure(client):
    assert login(client, password="wrong").status_code == 200
    assert login(client).status_code == 302


def test_profile_requires_login(client):
    assert client.get("/profile").status_code == 302


def test_profile_when_logged_in(logged_in):
    body = logged_in.get("/profile").get_data(as_text=True)
    assert "alex.analyst@example.test" in body


def test_admin_status_requires_admin(logged_in):
    assert logged_in.get("/admin/status").status_code == 403


def test_admin_status_for_admin(client):
    login(client, username="admin")
    body = client.get("/admin/status").get_data(as_text=True)
    assert "Admin status" in body


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_valid_reorder_increases_stock(logged_in):
    token = csrf_token(logged_in, "/products/1")
    resp = logged_in.post("/products/1/reorder", data={"quantity": "5", "_csrf": token})
    assert resp.status_code == 302
    assert '<dd id="stock">47</dd>' in logged_in.get("/products/1").get_data(as_text=True)


def test_post_without_csrf_token_is_rejected(logged_in):
    assert logged_in.post("/products/1/reorder", data={"quantity": "5"}).status_code == 400


def test_security_headers(client):
    resp = client.get("/")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
