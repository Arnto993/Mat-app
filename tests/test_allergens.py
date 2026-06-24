from src.allergens import get_recipe_allergens, recipe_has_excluded_allergens


def test_get_recipe_allergens_detects_gluten():
    recipe = {
        "name": "Testpasta",
        "ingredients": {
            "pasta": 500
        }
    }

    allergens = get_recipe_allergens(recipe)

    assert "gluten" in allergens


def test_recipe_has_excluded_allergens_returns_true():
    recipe = {
        "name": "Testpasta",
        "ingredients": {
            "pasta": 500
        }
    }

    result = recipe_has_excluded_allergens(recipe, ["gluten"])

    assert result is True


def test_recipe_has_excluded_allergens_returns_false():
    recipe = {
        "name": "Risrett",
        "ingredients": {
            "ris": 400
        }
    }

    result = recipe_has_excluded_allergens(recipe, ["gluten"])

    assert result is False