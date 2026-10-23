from requests import RequestException


def test_external_barcode_success(client, monkeypatch):
    def fake_fetch(barcode):
        return {
            "name": "Sample Product",
            "barcode": barcode,
            "category": "Snacks",
            "description": "Demo",
        }

    monkeypatch.setattr("inventory_api.routes.fetch_product_by_barcode", fake_fetch)

    response = client.get("/external/barcode/12345")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Sample Product"


def test_external_barcode_not_found(client, monkeypatch):
    monkeypatch.setattr("inventory_api.routes.fetch_product_by_barcode", lambda _: None)

    response = client.get("/external/barcode/404")
    assert response.status_code == 404


def test_external_barcode_unavailable(client, monkeypatch):
    def raise_error(_):
        raise RequestException("API down")

    monkeypatch.setattr("inventory_api.routes.fetch_product_by_barcode", raise_error)
    response = client.get("/external/barcode/123")
    assert response.status_code == 503


def test_import_item_from_barcode(client, monkeypatch):
    monkeypatch.setattr(
        "inventory_api.routes.fetch_product_by_barcode",
        lambda barcode: {
            "name": "Imported Product",
            "barcode": barcode,
            "category": "Beverages",
            "description": "Imported",
        },
    )

    response = client.post("/items/import/barcode/999", json={"quantity": 12, "price": 5.75})
    assert response.status_code == 201
    item = response.get_json()
    assert item["name"] == "Imported Product"
    assert item["quantity"] == 12


def test_external_search_success(client, monkeypatch):
    monkeypatch.setattr(
        "inventory_api.routes.search_products_by_name",
        lambda query: [
            {"name": f"{query} A", "barcode": "1", "category": "C1", "description": None},
            {"name": f"{query} B", "barcode": "2", "category": "C2", "description": None},
        ],
    )

    response = client.get("/external/search?q=milk")
    assert response.status_code == 200
    assert len(response.get_json()) == 2
