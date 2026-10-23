import argparse
import json

import requests

BASE_URL = "http://127.0.0.1:5000"


def _print_response(response: requests.Response) -> None:
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print(response.text)


def cmd_list(_: argparse.Namespace) -> None:
    response = requests.get(f"{BASE_URL}/items", timeout=10)
    _print_response(response)


def cmd_get(args: argparse.Namespace) -> None:
    response = requests.get(f"{BASE_URL}/items/{args.id}", timeout=10)
    _print_response(response)


def cmd_add(args: argparse.Namespace) -> None:
    payload = {
        "name": args.name,
        "quantity": args.quantity,
        "price": args.price,
        "barcode": args.barcode,
        "category": args.category,
        "description": args.description,
    }
    response = requests.post(f"{BASE_URL}/items", json=payload, timeout=10)
    _print_response(response)


def cmd_update(args: argparse.Namespace) -> None:
    payload = {}
    for field in ["name", "quantity", "price", "barcode", "category", "description"]:
        value = getattr(args, field)
        if value is not None:
            payload[field] = value
    response = requests.patch(f"{BASE_URL}/items/{args.id}", json=payload, timeout=10)
    _print_response(response)


def cmd_delete(args: argparse.Namespace) -> None:
    response = requests.delete(f"{BASE_URL}/items/{args.id}", timeout=10)
    _print_response(response)


def cmd_external_barcode(args: argparse.Namespace) -> None:
    response = requests.get(f"{BASE_URL}/external/barcode/{args.barcode}", timeout=10)
    _print_response(response)


def cmd_external_search(args: argparse.Namespace) -> None:
    response = requests.get(f"{BASE_URL}/external/search", params={"q": args.query}, timeout=10)
    _print_response(response)


def cmd_import(args: argparse.Namespace) -> None:
    payload = {"quantity": args.quantity, "price": args.price}
    response = requests.post(f"{BASE_URL}/items/import/barcode/{args.barcode}", json=payload, timeout=10)
    _print_response(response)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for Flask Inventory API")
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="List all inventory items")
    list_cmd.set_defaults(func=cmd_list)

    get_cmd = sub.add_parser("get", help="Get one inventory item by id")
    get_cmd.add_argument("id", type=int)
    get_cmd.set_defaults(func=cmd_get)

    add_cmd = sub.add_parser("add", help="Add a new inventory item")
    add_cmd.add_argument("name")
    add_cmd.add_argument("quantity", type=int)
    add_cmd.add_argument("price", type=float)
    add_cmd.add_argument("--barcode")
    add_cmd.add_argument("--category")
    add_cmd.add_argument("--description")
    add_cmd.set_defaults(func=cmd_add)

    update_cmd = sub.add_parser("update", help="Update an inventory item")
    update_cmd.add_argument("id", type=int)
    update_cmd.add_argument("--name")
    update_cmd.add_argument("--quantity", type=int)
    update_cmd.add_argument("--price", type=float)
    update_cmd.add_argument("--barcode")
    update_cmd.add_argument("--category")
    update_cmd.add_argument("--description")
    update_cmd.set_defaults(func=cmd_update)

    delete_cmd = sub.add_parser("delete", help="Delete an inventory item")
    delete_cmd.add_argument("id", type=int)
    delete_cmd.set_defaults(func=cmd_delete)

    ext_barcode_cmd = sub.add_parser("external-barcode", help="Fetch OpenFoodFacts product by barcode")
    ext_barcode_cmd.add_argument("barcode")
    ext_barcode_cmd.set_defaults(func=cmd_external_barcode)

    ext_search_cmd = sub.add_parser("external-search", help="Search OpenFoodFacts products by name")
    ext_search_cmd.add_argument("query")
    ext_search_cmd.set_defaults(func=cmd_external_search)

    import_cmd = sub.add_parser("import-barcode", help="Import item from OpenFoodFacts into inventory")
    import_cmd.add_argument("barcode")
    import_cmd.add_argument("--quantity", type=int, default=1)
    import_cmd.add_argument("--price", type=float, default=0.0)
    import_cmd.set_defaults(func=cmd_import)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
