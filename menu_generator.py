from recipes import get_recipes

def generate_week_menu(number_of_people, taco_friday):
    recipes = get_recipes()

    menu = {
        "Mandag": recipes[0],
        "Tirsdag": recipes[1],
        "Onsdag": recipes[2],
        "Torsdag": recipes[3],
        "Fredag": recipes[4],
    }

    if taco_friday:
        taco = next(recipe for recipe in recipes if recipe["name"] == "Taco")
        menu["Fredag"] = taco

    return menu