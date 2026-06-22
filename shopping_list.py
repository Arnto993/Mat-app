def create_shopping_list(menu, number_of_people):
    shopping_list = {}

    for recipe in menu.values():
        base_servings = recipe.get("servings", 4)
        scale_factor = number_of_people / base_servings

        for ingredient, amount in recipe["ingredients"].items():
            scaled_amount = amount * scale_factor

            if ingredient in shopping_list:
                shopping_list[ingredient] += scaled_amount
            else:
                shopping_list[ingredient] = scaled_amount

    return shopping_list