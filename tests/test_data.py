from src.recipes import get_recipes
from src.products import get_products


def test_all_recipe_ingredients_exist_in_products():
    recipes = get_recipes()
    products = get_products()

    missing_ingredients = []

    for recipe in recipes:
        for ingredient in recipe["ingredients"]:
            product_id = ingredient["product_id"]

            if product_id not in products:
                missing_ingredients.append((recipe["name"], product_id))

    assert missing_ingredients == []


def test_all_recipes_have_required_fields():
    recipes = get_recipes()

    required_fields = [
        "id",
        "name",
        "servings",
        "difficulty",
        "time_minutes",
        "tags",
        "allergens",
        "ingredients"
    ]

    missing_fields = []

    for recipe in recipes:
        for field in required_fields:
            if field not in recipe:
                missing_fields.append((recipe.get("name", "Ukjent rett"), field))

    assert missing_fields == []


def test_all_recipe_ingredients_have_required_fields_and_matching_units():
    recipes = get_recipes()
    products = get_products()

    required_fields = ["product_id", "amount", "unit"]
    invalid_ingredients = []

    for recipe in recipes:
        for ingredient in recipe["ingredients"]:
            for field in required_fields:
                if field not in ingredient:
                    invalid_ingredients.append((recipe["name"], ingredient, field))

            product = products.get(ingredient.get("product_id"))
            if product is not None and ingredient.get("unit") != product["unit"]:
                invalid_ingredients.append((
                    recipe["name"],
                    ingredient["product_id"],
                    "unit"
                ))

    assert invalid_ingredients == []


def test_all_products_have_required_fields():
    products = get_products()
    required_fields = [
        "name",
        "category",
        "price_nok",
        "package_size",
        "unit",
        "allergens",
        "is_basic",
        "is_fresh",
        "cost_mode"
    ]
    missing_fields = []

    for product_id, product in products.items():
        for field in required_fields:
            if field not in product:
                missing_fields.append((product_id, field))

    assert missing_fields == []
