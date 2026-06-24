from src.recipes import get_recipes
from src.products import get_products


def test_all_recipe_ingredients_exist_in_products():
    recipes = get_recipes()
    products = get_products()

    missing_ingredients = []

    for recipe in recipes:
        for ingredient in recipe["ingredients"]:
            if ingredient not in products:
                missing_ingredients.append((recipe["name"], ingredient))

    assert missing_ingredients == []

def test_all_recipes_have_required_fields():
    recipes = get_recipes()

    required_fields = [
        "name",
        "servings",
        "category",
        "tags",
        "contains_fish",
        "vegetarian",
        "healthy_score",
        "difficulty",
        "time_minutes",
        "calories_per_portion",
        "ingredients"
    ]

    missing_fields = []

    for recipe in recipes:
        for field in required_fields:
            if field not in recipe:
                missing_fields.append((recipe.get("name", "Ukjent rett"), field))

    assert missing_fields == []