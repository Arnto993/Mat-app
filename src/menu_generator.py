import random

from src.recipes import get_recipes
from src.shopping_list import create_rounded_shopping_list
from src.price_calculator import calculate_total_price_from_shopping_list
from src.allergens import recipe_has_excluded_allergens


DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]
MENU_PRIORITY_NONE = None
MENU_PRIORITY_CHEAPEST = "cheapest"
MENU_PRIORITY_FASTEST = "fastest"
MENU_PRIORITY_HEALTHIER = "healthier"
PRIORITIZED_POOL_MIN_EXTRA = 3
PRIORITIZED_POOL_SHARE = 0.4


def get_menu_priority(preferences):
    priority = preferences.get("menu_priority")

    if priority in {
        MENU_PRIORITY_CHEAPEST,
        MENU_PRIORITY_FASTEST,
        MENU_PRIORITY_HEALTHIER
    }:
        return priority

    return MENU_PRIORITY_NONE


def find_recipe_by_name(recipes, name):
    for recipe in recipes:
        if recipe["name"].lower() == name.lower():
            return recipe

    return None


def recipe_contains_fish(recipe):
    return recipe.get("contains_fish", False) or recipe.get("category") == "fisk"


def has_fish(menu):
    return any(
        recipe_contains_fish(recipe)
        for recipe in menu.values()
    )


def calculate_menu_time(menu):
    return sum(
        recipe.get("time_minutes", 999)
        for recipe in menu.values()
    )


def calculate_menu_health_score(menu):
    if not menu:
        return 0

    return sum(
        recipe.get("healthy_score", 0)
        for recipe in menu.values()
    ) / len(menu)


def calculate_menu_calories(menu):
    return sum(
        recipe.get("calories_per_portion", 999)
        for recipe in menu.values()
    )


def calculate_menu_recipe_price(menu):
    return sum(
        recipe.get("estimated_price", 999)
        for recipe in menu.values()
    )


def get_recipe_tags(recipe):
    return {
        tag.lower()
        for tag in recipe.get("tags", [])
    }


def get_recipe_priority_score(recipe, priority):
    tags = get_recipe_tags(recipe)

    if priority == MENU_PRIORITY_CHEAPEST:
        score = -recipe.get("estimated_price", 999)

        if "billig" in tags:
            score += 25
        if "student" in tags:
            score += 5

        return score

    if priority == MENU_PRIORITY_FASTEST:
        score = -recipe.get("time_minutes", 999)

        if "rask" in tags:
            score += 10
        if "enkel" in tags or "lett" in tags:
            score += 4

        return score

    if priority == MENU_PRIORITY_HEALTHIER:
        score = recipe.get("healthy_score", 0) * 100
        score -= recipe.get("calories_per_portion", 999) / 20

        if "sunn" in tags:
            score += 25
        if "protein" in tags:
            score += 8

        return score

    return 0


def get_prioritized_recipe_pool(recipes, priority, count):
    if priority is MENU_PRIORITY_NONE:
        return recipes.copy()

    sorted_recipes = sorted(
        recipes,
        key=lambda recipe: get_recipe_priority_score(recipe, priority),
        reverse=True
    )
    pool_size = max(
        count + PRIORITIZED_POOL_MIN_EXTRA,
        int(len(sorted_recipes) * PRIORITIZED_POOL_SHARE)
    )

    return sorted_recipes[:min(len(sorted_recipes), pool_size)]


def weighted_sample_without_replacement(recipes, count):
    selected_recipes = []
    available_recipes = recipes.copy()

    for _ in range(count):
        weights = list(range(len(available_recipes), 0, -1))
        selected_recipe = random.choices(available_recipes, weights=weights, k=1)[0]

        selected_recipes.append(selected_recipe)
        available_recipes.remove(selected_recipe)

    return selected_recipes


def select_recipes_for_menu(recipes, count, priority):
    if len(recipes) < count:
        return None

    if priority is MENU_PRIORITY_NONE:
        return random.sample(recipes, count)

    recipe_pool = get_prioritized_recipe_pool(recipes, priority, count)

    if len(recipe_pool) < count:
        return None

    return weighted_sample_without_replacement(recipe_pool, count)


def filter_recipes(recipes, preferences):
    filtered_recipes = []

    for recipe in recipes:
        if preferences.get("wants_fish") is False and recipe_contains_fish(recipe):
            continue

        if preferences.get("vegetarian_only") and not recipe.get("vegetarian", False):
            continue

        max_time = preferences.get("max_time_minutes")
        if max_time is not None and recipe.get("time_minutes", 999) > max_time:
            continue

        avoid_categories = preferences.get("avoid_categories", [])
        if recipe.get("category") in avoid_categories:
            continue

        excluded_allergens = preferences.get("excluded_allergens", [])
        if recipe_has_excluded_allergens(recipe, excluded_allergens):
            continue

        filtered_recipes.append(recipe)

    return filtered_recipes


def menu_matches_preferences(menu, preferences):
    # Hvis brukeren vil ha fisk, må menyen inneholde minst én fiskerett
    if preferences.get("wants_fish") is True and not has_fish(menu):
        return False

    # Hvis brukeren ikke vil ha fisk, skal menyen ikke ha fisk
    if preferences.get("wants_fish") is False and has_fish(menu):
        return False

    return True


def generate_week_menu(recipes, taco_friday=True, priority=MENU_PRIORITY_NONE):
    menu = {}
    available_recipes = recipes.copy()

    if taco_friday:
        taco = find_recipe_by_name(available_recipes, "Taco")

        if taco is None:
            return None

        menu["Fredag"] = taco
        available_recipes.remove(taco)

    days_to_fill = [day for day in DAYS if day not in menu]

    if len(available_recipes) < len(days_to_fill):
        return None

    selected_recipes = select_recipes_for_menu(
        available_recipes,
        len(days_to_fill),
        priority
    )

    if selected_recipes is None:
        return None

    for day, recipe in zip(days_to_fill, selected_recipes):
        menu[day] = recipe

    return menu


def generate_menu_with_budget(
    number_of_people,
    taco_friday,
    max_budget,
    preferences,
    max_attempts=100,
    pantry_items=None
):
    recipes = get_recipes()
    available_recipes = filter_recipes(recipes, preferences)
    menu_priority = get_menu_priority(preferences)

    for attempt in range(max_attempts):
        menu = generate_week_menu(available_recipes, taco_friday, menu_priority)

        if menu is None:
            return None, None, None

        if not menu_matches_preferences(menu, preferences):
            continue

        shopping_list = create_rounded_shopping_list(
            menu,
            number_of_people,
            pantry_items
        )
        total_price = calculate_total_price_from_shopping_list(shopping_list)

        if total_price <= max_budget:
            return menu, shopping_list, total_price

    return None, None, None
