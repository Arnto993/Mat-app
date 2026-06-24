import json


def get_recipes():
    with open("data/recipes.json", "r", encoding="utf-8") as file:
        recipes = json.load(file)

    return recipes