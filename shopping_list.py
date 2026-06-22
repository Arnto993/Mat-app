import math
from products import get_products


def create_raw_shopping_list(menu, number_of_people):
    shopping_list = {}

    for recipe in menu.values():
        base_servings = recipe.get("servings", 4)
        scale_factor = number_of_people / base_servings

        for ingredient, amount in recipe["ingredients"].items():
            scaled_amount = amount * scale_factor

            if ingredient in shopping_list:
                shopping_list[ingredient] += scaled_amount
            else:
                shopping_list[ingredient] = scaled_amount

    return shopping_list


def create_rounded_shopping_list(menu, number_of_people):
    raw_list = create_raw_shopping_list(menu, number_of_people)
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