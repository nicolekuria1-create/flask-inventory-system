from urllib.parse import quote

import requests

OPEN_FOOD_FACTS_PRODUCT = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
OPEN_FOOD_FACTS_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1&page_size=10"


def fetch_product_by_barcode(barcode: str) -> dict | None:
    response = requests.get(OPEN_FOOD_FACTS_PRODUCT.format(barcode=quote(barcode)), timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != 1:
        return None

    product = data.get("product", {})
    return {
        "name": product.get("product_name") or "Unknown product",
        "barcode": barcode,
        "category": product.get("categories"),
        "description": product.get("generic_name") or product.get("ingredients_text"),
    }


def search_products_by_name(name: str) -> list[dict]:
    response = requests.get(OPEN_FOOD_FACTS_SEARCH.format(query=quote(name)), timeout=10)
    response.raise_for_status()
    data = response.json()

    products = []
    for product in data.get("products", []):
        barcode = product.get("code")
        products.append(
            {
                "name": product.get("product_name") or "Unknown product",
                "barcode": barcode,
                "category": product.get("categories"),
                "description": product.get("generic_name") or product.get("ingredients_text"),
            }
        )
    return products
