import json


def get_recipes():
    with open("data/recipes.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("recipes", data)
