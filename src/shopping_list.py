import math
from src.products import get_products


PACKAGE_COST_MODE = "package"
PANTRY_PRORATED_COST_MODE = "pantry_prorated"
OTHER_SHOPPING_CATEGORY = "Annet"

SHOPPING_CATEGORY_ORDER = [
    "Frukt og grønt",
    "Brød og bakervarer",
    "Kjøtt, fisk og pålegg",
    "Meieri og egg",
    "Tørrvarer",
    "Hermetikk og glass",
    "Saus, krydder og basisvarer",
    "Frysevarer",
    "Drikke",
    "Snacks og søtsaker",
    "Husholdning og hygiene",
    OTHER_SHOPPING_CATEGORY
]

PRODUCT_CATEGORY_TO_SHOPPING_CATEGORY = {
    "Frukt og grønt": "Frukt og grønt",
    "Kjøtt": "Kjøtt, fisk og pålegg",
    "Fisk": "Kjøtt, fisk og pålegg",
    "Vegetarprotein": "Kjøtt, fisk og pålegg",
    "Meieri og egg": "Meieri og egg",
    "Tørrvarer": "Tørrvarer",
    "Hermetikk": "Hermetikk og glass",
    "Saus og dressing": "Saus, krydder og basisvarer",
    "Krydder": "Saus, krydder og basisvarer",
    "Basisvarer": "Saus, krydder og basisvarer"
}


def iter_recipe_ingredients(recipe):
    ingredients = recipe["ingredients"]

    if hasattr(ingredients, "items"):
        for product_id, amount in ingredients.items():
            yield product_id, amount, None
        return

    for ingredient in ingredients:
        yield ingredient["product_id"], ingredient["amount"], ingredient.get("unit")


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


def product_is_frozen(product_id, product):
    name = product.get("name", "").lower()
    display_name = product.get("display_name", "").lower()

    return (
        "frozen" in product_id
        or "fryst" in name
        or "fryst" in display_name
    )


def get_shopping_category(product_id, product):
    if product_is_frozen(product_id, product):
        return "Frysevarer"

    return PRODUCT_CATEGORY_TO_SHOPPING_CATEGORY.get(
        product.get("category"),
        product.get("category", OTHER_SHOPPING_CATEGORY)
    )


def get_shopping_category_sort_key(category):
    try:
        return SHOPPING_CATEGORY_ORDER.index(category)
    except ValueError:
        return SHOPPING_CATEGORY_ORDER.index(OTHER_SHOPPING_CATEGORY)


def sort_shopping_list(shopping_list):
    return dict(
        sorted(
            shopping_list.items(),
            key=lambda item: (
                get_shopping_category_sort_key(
                    item[1].get("shopping_category", OTHER_SHOPPING_CATEGORY)
                ),
                item[1].get("shopping_category", OTHER_SHOPPING_CATEGORY).lower(),
                item[1].get("display_name", item[0]).lower()
            )
        )
    )


def group_shopping_list_by_category(shopping_list):
    grouped_list = []
    current_category = None
    current_items = []

    for item in sort_shopping_list(shopping_list).values():
        category = item.get("shopping_category", OTHER_SHOPPING_CATEGORY)

        if category != current_category:
            if current_items:
                grouped_list.append((current_category, current_items))

            current_category = category
            current_items = []

        current_items.append(item)

    if current_items:
        grouped_list.append((current_category, current_items))

    return grouped_list


def create_raw_shopping_list(menu, number_of_people, pantry_items=None):
    shopping_list = {}
    pantry_items = normalize_pantry_items(pantry_items)

    for recipe in menu.values():
        base_servings = recipe.get("servings", 4)
        scale_factor = number_of_people / base_servings

        for ingredient, amount, _unit in iter_recipe_ingredients(recipe):
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
        price = product.get("price_nok", product.get("estimated_package_price", 0))
        cost_mode = product.get("cost_mode", PACKAGE_COST_MODE)

        if cost_mode == PANTRY_PRORATED_COST_MODE:
            packages_needed = needed_amount / package_size
        else:
            packages_needed = math.ceil(needed_amount / package_size)

        estimated_total_price = round(packages_needed * price, 2)

        rounded_list[ingredient] = {
            "product_id": ingredient,
            "display_name": product.get("display_name", product["name"]),
            "shopping_category": get_shopping_category(ingredient, product),
            "needed_amount": needed_amount,
            "unit": product["unit"],
            "packages_needed": packages_needed,
            "package_size": package_size,
            "package_unit": product.get("package_unit", "pakke"),
            "estimated_total_price": estimated_total_price,
            "cost_mode": cost_mode
        }

    return sort_shopping_list(rounded_list)

def calculate_total_price_from_shopping_list(shopping_list):
    total_price = 0

    for item in shopping_list.values():
        total_price += item["estimated_total_price"]

    return total_price
