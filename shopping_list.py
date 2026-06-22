def create_shopping_list(menu):
    shopping_list = {}

    for recipe in menu.values():
        for ingredient, amount in recipe["ingredients"].items():
            if ingredient in shopping_list:
                shopping_list[ingredient] += amount
            else:
                shopping_list[ingredient] = amount

    return shopping_list