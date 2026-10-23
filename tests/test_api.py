def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Inventory API is running"


def test_create_and_get_item(client):
    payload = {"name": "Rice", "quantity": 10, "price": 4.5}
    create_res = client.post("/items", json=payload)

    assert create_res.status_code == 201
    item = create_res.get_json()
    assert item["name"] == "Rice"

    get_res = client.get(f"/items/{item['id']}")
    assert get_res.status_code == 200
    assert get_res.get_json()["quantity"] == 10


def test_list_items(client):
    client.post("/items", json={"name": "Sugar", "quantity": 3, "price": 2.0})
    response = client.get("/items")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_patch_item(client):
    create_res = client.post("/items", json={"name": "Tea", "quantity": 5, "price": 1.5})
    item_id = create_res.get_json()["id"]

    patch_res = client.patch(f"/items/{item_id}", json={"quantity": 8, "price": 2.25})
    assert patch_res.status_code == 200
    assert patch_res.get_json()["quantity"] == 8
    assert patch_res.get_json()["price"] == 2.25


def test_delete_item(client):
    create_res = client.post("/items", json={"name": "Soap", "quantity": 7, "price": 3.0})
    item_id = create_res.get_json()["id"]

    delete_res = client.delete(f"/items/{item_id}")
    assert delete_res.status_code == 200

    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 404


def test_create_requires_fields(client):
    response = client.post("/items", json={"name": "Invalid"})
    assert response.status_code == 400


def test_external_search_requires_query(client):
    response = client.get("/external/search")
    assert response.status_code == 400
