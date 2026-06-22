import random
from recipes import get_recipes


DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]


def find_recipe_by_name(recipes, name):
    for recipe in recipes:
        if recipe["name"].lower() == name.lower():
            return recipe

    return None


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