from src.menu_generator import (
    MENU_PRIORITY_CHEAPEST,
    MENU_PRIORITY_FASTEST,
    MENU_PRIORITY_HEALTHIER,
    get_prioritized_recipe_pool,
    get_recipe_priority_score,
    has_fish
)


def test_has_fish_returns_true_when_menu_contains_fish():
    menu = {
        "Mandag": {
            "name": "Laks med ris",
            "category": "fisk",
            "contains_fish": True
        },
        "Tirsdag": {
            "name": "Pasta",
            "category": "pasta",
            "contains_fish": False
        }
    }

    assert has_fish(menu) is True


def test_has_fish_returns_false_when_menu_has_no_fish():
    menu = {
        "Mandag": {
            "name": "Pasta",
            "category": "pasta",
            "contains_fish": False
        }
    }

    assert has_fish(menu) is False


def test_recipe_priority_score_uses_price_and_cheap_tag():
    cheap_recipe = {
        "name": "Billig middag",
        "tags": ["billig"],
        "estimated_price": 90
    }
    expensive_recipe = {
        "name": "Dyr middag",
        "tags": [],
        "estimated_price": 130
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
        "tags": ["sunn"],
        "healthy_score": 5,
        "calories_per_portion": 550
    }
    less_healthy_recipe = {
        "name": "Mindre sunn middag",
        "tags": [],
        "healthy_score": 3,
        "calories_per_portion": 700
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
