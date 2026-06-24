import random
from recipes import get_recipes
from shopping_list import create_rounded_shopping_list, calculate_total_price_from_shopping_list


DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]


def find_recipe_by_name(recipes, name):
    for recipe in recipes:
        if recipe["name"].lower() == name.lower():
            return recipe

    return None

def has_fish(menu):
    return any(
        recipe.get("category") == "fisk"
        for recipe in menu.values()
    )

def generate_week_menu(taco_friday=True):
    recipes = get_recipes()
    menu = {}

    available_recipes = recipes.copy()

    if taco_friday:
        taco = find_recipe_by_name(available_recipes, "Taco")

        if taco is not None:
            menu["Fredag"] = taco
            available_recipes.remove(taco)

    days_to_fill = [day for day in DAYS if day not in menu]

    if len(available_recipes) < len(days_to_fill):
        raise ValueError("Ikke nok oppskrifter til å lage ukesmeny.")

    selected_recipes = random.sample(available_recipes, len(days_to_fill))

    for day, recipe in zip(days_to_fill, selected_recipes):
        menu[day] = recipe

    return menu

def generate_menu_with_budget(
    number_of_people,
    taco_friday,
    max_budget,
    wants_fish,
    max_attempts=100
):
    for attempt in range(max_attempts):
        menu = generate_week_menu(taco_friday)

        if has_fish(menu) != wants_fish:
            continue

        shopping_list = create_rounded_shopping_list(menu, number_of_people)
        total_price = calculate_total_price_from_shopping_list(shopping_list)

        if total_price <= max_budget:
            return menu, shopping_list, total_price

    return None, None, None