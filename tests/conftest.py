import pytest

from inventory_api import create_app
from inventory_api.store import InventoryStore


@pytest.fixture
def client(monkeypatch):
    app = create_app({"TESTING": True})

    # Isolate tests from shared in-memory store.
    test_store = InventoryStore()
    monkeypatch.setattr("inventory_api.routes.inventory_store", test_store)

    with app.test_client() as client:
        yield client
