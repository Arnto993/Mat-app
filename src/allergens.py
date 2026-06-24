from src.products import get_products


def get_recipe_allergens(recipe):
    products = get_products()
    allergens = set()

    for ingredient in recipe["ingredients"]:
        product = products.get(ingredient)

        if product is None:
            continue

        for allergen in product.get("allergens", []):
            allergens.add(allergen)

    return allergens


def recipe_has_excluded_allergens(recipe, excluded_allergens):
    recipe_allergens = get_recipe_allergens(recipe)

    for allergen in excluded_allergens:
        if allergen in recipe_allergens:
            return True

    return False