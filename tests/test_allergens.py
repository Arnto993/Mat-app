from src.allergens import get_recipe_allergens, recipe_has_excluded_allergens


def test_get_recipe_allergens_detects_gluten():
    recipe = {
        "name": "Testpasta",
        "ingredients": [
            {"product_id": "pasta_spaghetti_500", "amount": 500, "unit": "g"}
        ]
    }

    allergens = get_recipe_allergens(recipe)

    assert "gluten" in allergens


def test_recipe_has_excluded_allergens_returns_true():
    recipe = {
        "name": "Testpasta",
        "ingredients": [
            {"product_id": "pasta_spaghetti_500", "amount": 500, "unit": "g"}
        ]
    }

    result = recipe_has_excluded_allergens(recipe, ["gluten"])

    assert result is True


def test_recipe_has_excluded_allergens_returns_false():
    recipe = {
        "name": "Risrett",
        "ingredients": [
            {"product_id": "rice_jasmin_1000", "amount": 400, "unit": "g"}
        ]
    }

    result = recipe_has_excluded_allergens(recipe, ["gluten"])

    assert result is False
