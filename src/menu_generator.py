import random

from src.recipes import get_recipes
from src.shopping_list import create_rounded_shopping_list
from src.price_calculator import calculate_total_price_from_shopping_list
from src.allergens import recipe_has_excluded_allergens


DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]


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


def generate_week_menu(recipes, taco_friday=True):
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

    selected_recipes = random.sample(available_recipes, len(days_to_fill))

    for day, recipe in zip(days_to_fill, selected_recipes):
        menu[day] = recipe

    return menu


def generate_menu_with_budget(
    number_of_people,
    taco_friday,
    max_budget,
    preferences,
    max_attempts=100
):
    recipes = get_recipes()
    available_recipes = filter_recipes(recipes, preferences)

    for attempt in range(max_attempts):
        menu = generate_week_menu(available_recipes, taco_friday)

        if menu is None:
            return None, None, None

        if not menu_matches_preferences(menu, preferences):
            continue

        shopping_list = create_rounded_shopping_list(menu, number_of_people)
        total_price = calculate_total_price_from_shopping_list(shopping_list)

        if total_price <= max_budget:
            return menu, shopping_list, total_price

    return None, None, None