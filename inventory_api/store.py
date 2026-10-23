from threading import Lock


class InventoryStore:
    def __init__(self) -> None:
        self._items: list[dict] = []
        self._next_id = 1
        self._lock = Lock()

    def list_items(self) -> list[dict]:
        return [item.copy() for item in self._items]

    def get_item(self, item_id: int) -> dict | None:
        item = next((i for i in self._items if i["id"] == item_id), None)
        return item.copy() if item else None

    def create_item(self, payload: dict) -> dict:
        with self._lock:
            item = {
                "id": self._next_id,
                "name": payload["name"],
                "quantity": int(payload["quantity"]),
                "price": float(payload["price"]),
                "barcode": payload.get("barcode"),
                "category": payload.get("category"),
                "description": payload.get("description"),
            }
            self._items.append(item)
            self._next_id += 1
            return item.copy()

    def update_item(self, item_id: int, payload: dict) -> dict | None:
        with self._lock:
            item = next((i for i in self._items if i["id"] == item_id), None)
            if not item:
                return None

            allowed_fields = {
                "name": str,
                "quantity": int,
                "price": float,
                "barcode": (str, type(None)),
                "category": (str, type(None)),
                "description": (str, type(None)),
            }

            for field, value in payload.items():
                if field in allowed_fields:
                    if field == "quantity":
                        item[field] = int(value)
                    elif field == "price":
                        item[field] = float(value)
                    else:
                        item[field] = value
            return item.copy()

    def delete_item(self, item_id: int) -> bool:
        with self._lock:
            index = next((idx for idx, i in enumerate(self._items) if i["id"] == item_id), None)
            if index is None:
                return False
            self._items.pop(index)
            return True


inventory_store = InventoryStore()
