import math
from src.products import get_products


def normalize_pantry_items(pantry_items):
    if pantry_items is None:
        return {}

    if hasattr(pantry_items, "items"):
        return {
            item: max(0, float(amount))
            for item, amount in pantry_items.items()
            if item and amount
        }

    return {
        item: math.inf
        for item in pantry_items
        if item
    }


def create_raw_shopping_list(menu, number_of_people, pantry_items=None):
    shopping_list = {}
    pantry_items = normalize_pantry_items(pantry_items)

    for recipe in menu.values():
        base_servings = recipe.get("servings", 4)
        scale_factor = number_of_people / base_servings

        for ingredient, amount in recipe["ingredients"].items():
            scaled_amount = amount * scale_factor

            if ingredient in shopping_list:
                shopping_list[ingredient] += scaled_amount
            else:
                shopping_list[ingredient] = scaled_amount

    for ingredient, pantry_amount in pantry_items.items():
        if ingredient not in shopping_list:
            continue

        if pantry_amount >= shopping_list[ingredient]:
            del shopping_list[ingredient]
        else:
            shopping_list[ingredient] -= pantry_amount

    return shopping_list


def create_rounded_shopping_list(menu, number_of_people, pantry_items=None):
    raw_list = create_raw_shopping_list(menu, number_of_people, pantry_items)
    products = get_products()

    rounded_list = {}

    for ingredient, needed_amount in raw_list.items():
        product = products[ingredient]

        package_size = product["package_size"]
        packages_needed = math.ceil(needed_amount / package_size)

        estimated_total_price = packages_needed * product["estimated_package_price"]

        rounded_list[ingredient] = {
            "display_name": product["display_name"],
            "needed_amount": needed_amount,
            "unit": product["unit"],
            "packages_needed": packages_needed,
            "package_size": package_size,
            "package_unit": product["package_unit"],
            "estimated_total_price": estimated_total_price
        }

    return rounded_list

def calculate_total_price_from_shopping_list(shopping_list):
    total_price = 0

    for item in shopping_list.values():
        total_price += item["estimated_total_price"]

    return total_price
