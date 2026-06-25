from src.products import get_products
from src.shopping_list import iter_recipe_ingredients


def get_recipe_allergens(recipe):
    products = get_products()
    allergens = set(recipe.get("allergens", []))

    for product_id, _amount, _unit in iter_recipe_ingredients(recipe):
        product = products.get(product_id)

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
