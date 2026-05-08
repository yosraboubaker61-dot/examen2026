import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, products, next_id


@pytest.fixture(autouse=True)
def reset_state():
    """Reset in-memory DB before each test."""
    global next_id
    import app as app_module
    app_module.products.clear()
    app_module.products.extend([
        {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 10},
        {"id": 2, "name": "Mouse",  "price": 25.50,  "quantity": 50},
    ])
    app_module.next_id = 3
    yield


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── GET /products ──────────────────────────────────────────────────────────────
class TestGetProducts:
    def test_get_all_returns_200(self, client):
        r = client.get("/products")
        assert r.status_code == 200

    def test_get_all_returns_list(self, client):
        data = r = client.get("/products").get_json()
        assert isinstance(data, list)

    def test_get_all_initial_count(self, client):
        data = client.get("/products").get_json()
        assert len(data) == 2


# ── GET /products/<id> ─────────────────────────────────────────────────────────
class TestGetProduct:
    def test_get_existing(self, client):
        r = client.get("/products/1")
        assert r.status_code == 200
        assert r.get_json()["name"] == "Laptop"

    def test_get_nonexistent_returns_404(self, client):
        r = client.get("/products/999")
        assert r.status_code == 404

    def test_get_404_has_error_key(self, client):
        r = client.get("/products/999")
        assert "error" in r.get_json()


# ── POST /products ─────────────────────────────────────────────────────────────
class TestCreateProduct:
    def test_create_valid(self, client):
        r = client.post("/products",
                        data=json.dumps({"name": "Keyboard", "price": 79.99}),
                        content_type="application/json")
        assert r.status_code == 201

    def test_create_returns_new_product(self, client):
        r = client.post("/products",
                        data=json.dumps({"name": "Keyboard", "price": 79.99}),
                        content_type="application/json")
        data = r.get_json()
        assert data["name"] == "Keyboard"
        assert data["id"] == 3

    def test_create_missing_name_returns_400(self, client):
        r = client.post("/products",
                        data=json.dumps({"price": 10}),
                        content_type="application/json")
        assert r.status_code == 400

    def test_create_missing_price_returns_400(self, client):
        r = client.post("/products",
                        data=json.dumps({"name": "Widget"}),
                        content_type="application/json")
        assert r.status_code == 400

    def test_create_with_quantity(self, client):
        r = client.post("/products",
                        data=json.dumps({"name": "Monitor", "price": 299, "quantity": 5}),
                        content_type="application/json")
        assert r.get_json()["quantity"] == 5


# ── PUT /products/<id> ─────────────────────────────────────────────────────────
class TestUpdateProduct:
    def test_update_existing(self, client):
        r = client.put("/products/1",
                       data=json.dumps({"price": 1199.99}),
                       content_type="application/json")
        assert r.status_code == 200
        assert r.get_json()["price"] == 1199.99

    def test_update_nonexistent_returns_404(self, client):
        r = client.put("/products/999",
                       data=json.dumps({"name": "Ghost"}),
                       content_type="application/json")
        assert r.status_code == 404

    def test_update_preserves_unchanged_fields(self, client):
        client.put("/products/1",
                   data=json.dumps({"price": 888}),
                   content_type="application/json")
        r = client.get("/products/1")
        assert r.get_json()["name"] == "Laptop"


# ── DELETE /products/<id> ──────────────────────────────────────────────────────
class TestDeleteProduct:
    def test_delete_existing(self, client):
        r = client.delete("/products/1")
        assert r.status_code == 200

    def test_delete_removes_product(self, client):
        client.delete("/products/1")
        r = client.get("/products/1")
        assert r.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        r = client.delete("/products/999")
        assert r.status_code == 404


# ── Health check ───────────────────────────────────────────────────────────────
class TestHealth:
    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_status_ok(self, client):
        assert client.get("/health").get_json()["status"] == "ok"
