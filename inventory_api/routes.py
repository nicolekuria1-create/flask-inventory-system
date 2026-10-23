from flask import Blueprint, jsonify, request
from requests import RequestException

from .external_api import fetch_product_by_barcode, search_products_by_name
from .store import inventory_store

inventory_bp = Blueprint("inventory", __name__)


def _validate_create_payload(payload: dict) -> tuple[bool, str | None]:
    required = ["name", "quantity", "price"]
    missing = [field for field in required if field not in payload]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    try:
        int(payload["quantity"])
        float(payload["price"])
    except (ValueError, TypeError):
        return False, "Fields 'quantity' and 'price' must be numeric"

    return True, None


@inventory_bp.route("/", methods=["GET"])
def health_check():
    return jsonify({"message": "Inventory API is running"}), 200


@inventory_bp.route("/items", methods=["GET"])
def list_items():
    return jsonify(inventory_store.list_items()), 200


@inventory_bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id: int):
    item = inventory_store.get_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@inventory_bp.route("/items", methods=["POST"])
def create_item():
    payload = request.get_json(silent=True) or {}
    valid, error = _validate_create_payload(payload)
    if not valid:
        return jsonify({"error": error}), 400

    item = inventory_store.create_item(payload)
    return jsonify(item), 201


@inventory_bp.route("/items/<int:item_id>", methods=["PATCH"])
def patch_item(item_id: int):
    payload = request.get_json(silent=True) or {}
    if not payload:
        return jsonify({"error": "No data supplied"}), 400

    item = inventory_store.update_item(item_id, payload)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@inventory_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id: int):
    deleted = inventory_store.delete_item(item_id)
    if not deleted:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"message": "Item deleted"}), 200


@inventory_bp.route("/external/barcode/<string:barcode>", methods=["GET"])
def external_by_barcode(barcode: str):
    try:
        product = fetch_product_by_barcode(barcode)
    except RequestException:
        return jsonify({"error": "External API unavailable"}), 503

    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200


@inventory_bp.route("/external/search", methods=["GET"])
def external_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    try:
        products = search_products_by_name(query)
    except RequestException:
        return jsonify({"error": "External API unavailable"}), 503

    return jsonify(products), 200


@inventory_bp.route("/items/import/barcode/<string:barcode>", methods=["POST"])
def import_item_by_barcode(barcode: str):
    payload = request.get_json(silent=True) or {}
    quantity = payload.get("quantity", 1)
    price = payload.get("price", 0.0)

    try:
        quantity = int(quantity)
        price = float(price)
    except (TypeError, ValueError):
        return jsonify({"error": "Fields 'quantity' and 'price' must be numeric"}), 400

    try:
        product = fetch_product_by_barcode(barcode)
    except RequestException:
        return jsonify({"error": "External API unavailable"}), 503

    if not product:
        return jsonify({"error": "Product not found"}), 404

    new_item = inventory_store.create_item(
        {
            "name": product["name"],
            "quantity": quantity,
            "price": price,
            "barcode": product.get("barcode"),
            "category": product.get("category"),
            "description": product.get("description"),
        }
    )
    return jsonify(new_item), 201
