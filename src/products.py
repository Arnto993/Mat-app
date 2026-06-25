import json


def get_products():
    with open("data/products.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("products", data)
