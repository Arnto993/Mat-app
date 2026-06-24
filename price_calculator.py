def calculate_total_price_from_shopping_list(shopping_list):
    total_price = 0

    for item in shopping_list.values():
        total_price += item["estimated_total_price"]

    return total_price