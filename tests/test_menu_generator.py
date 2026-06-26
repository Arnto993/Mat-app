from src.menu_generator import (
    MENU_PRIORITY_CHEAPEST,
    MENU_PRIORITY_FASTEST,
    MENU_PRIORITY_HEALTHIER,
    MENU_PRIORITY_NONE,
    filter_recipes,
    get_replacement_recipe_candidates,
    get_prioritized_recipe_pool,
    get_recipe_pantry_usage_score,
    get_recipe_priority_score,
    has_fish,
    has_vegetarian,
    menu_matches_preferences,
    recipe_is_vegetarian
)


def test_has_fish_returns_true_when_menu_contains_fish():
    menu = {
        "Mandag": {
            "name": "Laks med ris",
            "tags": ["fisk"],
            "allergens": ["fish"],
            "ingredients": [
                {"product_id": "salmon_fillet_500", "amount": 500, "unit": "g"}
            ]
        },
        "Tirsdag": {
            "name": "Pasta",
            "tags": ["vegetar"],
            "allergens": ["gluten"],
            "ingredients": [
                {"product_id": "pasta_spaghetti_500", "amount": 400, "unit": "g"}
            ]
        }
    }

    assert has_fish(menu) is True


def test_has_fish_returns_false_when_menu_has_no_fish():
    menu = {
        "Mandag": {
            "name": "Pasta",
            "tags": ["vegetar"],
            "allergens": ["gluten"],
            "ingredients": [
                {"product_id": "pasta_spaghetti_500", "amount": 400, "unit": "g"}
            ]
        }
    }

    assert has_fish(menu) is False


def test_has_vegetarian_returns_true_when_menu_contains_vegetarian_recipe():
    menu = {
        "Mandag": {
            "name": "Vegetarrett",
            "tags": ["vegetar"]
        },
        "Tirsdag": {
            "name": "Kylling",
            "vegetarian": False
        }
    }

    assert has_vegetarian(menu) is True


def test_recipe_priority_score_uses_price_and_cheap_tag():
    cheap_recipe = {
        "name": "Billig middag",
        "tags": ["billig"],
        "ingredients": [
            {"product_id": "rice_jasmin_1000", "amount": 200, "unit": "g"}
        ]
    }
    expensive_recipe = {
        "name": "Dyr middag",
        "tags": [],
        "ingredients": [
            {"product_id": "salmon_fillet_500", "amount": 500, "unit": "g"}
        ]
    }

    cheap_score = get_recipe_priority_score(cheap_recipe, MENU_PRIORITY_CHEAPEST)
    expensive_score = get_recipe_priority_score(expensive_recipe, MENU_PRIORITY_CHEAPEST)

    assert cheap_score > expensive_score


def test_recipe_priority_score_uses_time_and_fast_tag():
    fast_recipe = {
        "name": "Rask middag",
        "tags": ["rask"],
        "time_minutes": 20
    }
    slow_recipe = {
        "name": "Langsom middag",
        "tags": [],
        "time_minutes": 35
    }

    fast_score = get_recipe_priority_score(fast_recipe, MENU_PRIORITY_FASTEST)
    slow_score = get_recipe_priority_score(slow_recipe, MENU_PRIORITY_FASTEST)

    assert fast_score > slow_score


def test_recipe_priority_score_uses_health_score_and_healthy_tag():
    healthy_recipe = {
        "name": "Sunn middag",
        "tags": ["sunnere", "vegetar"]
    }
    less_healthy_recipe = {
        "name": "Mindre sunn middag",
        "tags": []
    }

    healthy_score = get_recipe_priority_score(healthy_recipe, MENU_PRIORITY_HEALTHIER)
    less_healthy_score = get_recipe_priority_score(
        less_healthy_recipe,
        MENU_PRIORITY_HEALTHIER
    )

    assert healthy_score > less_healthy_score


def test_prioritized_recipe_pool_keeps_more_than_only_the_top_recipes():
    recipes = [
        {
            "name": f"Rett {number}",
            "tags": ["billig"] if number <= 3 else [],
            "estimated_price": 70 + number * 10
        }
        for number in range(1, 11)
    ]

    recipe_pool = get_prioritized_recipe_pool(
        recipes,
        MENU_PRIORITY_CHEAPEST,
        count=4
    )

    assert len(recipe_pool) > 4
    assert recipe_pool[0]["name"] == "Rett 1"


def test_recipe_pantry_usage_score_rewards_pantry_ingredients():
    pantry_recipe = {
        "name": "Risrett",
        "servings": 4,
        "ingredients": [
            {"product_id": "rice_jasmin_1000", "amount": 200, "unit": "g"}
        ]
    }
    other_recipe = {
        "name": "Pastarett",
        "servings": 4,
        "ingredients": [
            {"product_id": "pasta_spaghetti_500", "amount": 200, "unit": "g"}
        ]
    }

    pantry_items = {"rice_jasmin_1000": 200}

    assert (
        get_recipe_pantry_usage_score(pantry_recipe, pantry_items, 4)
        > get_recipe_pantry_usage_score(other_recipe, pantry_items, 4)
    )


def test_prioritized_recipe_pool_uses_pantry_when_no_priority_is_selected():
    recipes = [
        {
            "name": "Pastarett",
            "servings": 4,
            "ingredients": [
                {"product_id": "pasta_spaghetti_500", "amount": 200, "unit": "g"}
            ]
        },
        {
            "name": "Risrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 200, "unit": "g"}
            ]
        },
        {
            "name": "Linserett",
            "servings": 4,
            "ingredients": [
                {"product_id": "red_lentils_400", "amount": 200, "unit": "g"}
            ]
        }
    ]

    recipe_pool = get_prioritized_recipe_pool(
        recipes,
        MENU_PRIORITY_NONE,
        count=2,
        pantry_items={"rice_jasmin_1000": 200},
        number_of_people=4
    )

    assert recipe_pool[0]["name"] == "Risrett"


def test_recipe_is_vegetarian_uses_new_tags():
    recipe = {
        "name": "Vegetarrett",
        "tags": ["vegetar"],
        "ingredients": [
            {"product_id": "red_lentils_400", "amount": 300, "unit": "g"}
        ]
    }

    assert recipe_is_vegetarian(recipe) is True


def test_filter_recipes_excludes_vegetarian_when_requested():
    recipes = [
        {
            "name": "Vegetarrett",
            "vegetarian": True,
            "ingredients": []
        },
        {
            "name": "Kjottrett",
            "vegetarian": False,
            "ingredients": []
        }
    ]
    preferences = {
        "exclude_vegetarian": True
    }

    filtered_recipes = filter_recipes(recipes, preferences)

    assert [recipe["name"] for recipe in filtered_recipes] == ["Kjottrett"]


def test_menu_does_not_match_when_vegetarian_is_excluded_but_menu_has_vegetarian():
    menu = {
        "Mandag": {
            "name": "Vegetarrett",
            "vegetarian": True
        },
        "Tirsdag": {
            "name": "Kjottrett",
            "vegetarian": False
        }
    }
    preferences = {
        "exclude_vegetarian": True
    }

    assert menu_matches_preferences(menu, preferences) is False


def test_replacement_candidates_avoid_fish_next_to_fish():
    recipes = [
        {
            "id": "laks",
            "name": "Laks",
            "tags": ["fisk"],
            "ingredients": []
        },
        {
            "id": "torsk",
            "name": "Torsk",
            "tags": ["fisk"],
            "ingredients": []
        },
        {
            "id": "kylling",
            "name": "Kylling",
            "tags": ["kylling"],
            "ingredients": []
        },
        {
            "id": "pasta",
            "name": "Pasta",
            "tags": ["vegetar"],
            "ingredients": []
        }
    ]
    menu = {
        "Mandag": recipes[0],
        "Tirsdag": recipes[3],
        "Onsdag": recipes[1]
    }
    preferences = {
        "wants_fish": True
    }

    candidates = get_replacement_recipe_candidates(
        recipes,
        menu,
        "Tirsdag",
        preferences
    )

    assert [recipe["name"] for recipe in candidates] == ["Kylling"]


def test_replacement_candidates_keep_fish_when_replacing_only_fish_day():
    fish_recipe = {
        "id": "laks",
        "name": "Laks",
        "tags": ["fisk"],
        "ingredients": []
    }
    other_fish_recipe = {
        "id": "torsk",
        "name": "Torsk",
        "tags": ["fisk"],
        "ingredients": []
    }
    chicken_recipe = {
        "id": "kylling",
        "name": "Kylling",
        "tags": ["kylling"],
        "ingredients": []
    }
    menu = {
        "Mandag": fish_recipe,
        "Tirsdag": chicken_recipe
    }
    preferences = {
        "wants_fish": True
    }

    candidates = get_replacement_recipe_candidates(
        [fish_recipe, other_fish_recipe, chicken_recipe],
        menu,
        "Mandag",
        preferences
    )

    assert [recipe["name"] for recipe in candidates] == ["Torsk"]
