from menu_generator import generate_week_menu
from shopping_list import create_shopping_list


def calculate_total_price(menu, number_of_people):
    total_price = 0

    for recipe in menu.values():
        base_servings = recipe.get("servings", 4)
        scale_factor = number_of_people / base_servings
        total_price += recipe["estimated_price"] * scale_factor

    return total_price


def calculate_average_calories(menu):
    total_calories = 0

    for recipe in menu.values():
        total_calories += recipe["calories_per_portion"]

    return total_calories / len(menu)


def main():
    number_of_people = int(input("Hvor mange personer skal spise middag? "))

    taco_answer = input("Vil du ha taco på fredag? ja/nei: ").lower()
    taco_friday = taco_answer == "ja"

    menu = generate_week_menu(taco_friday)
    shopping_list = create_shopping_list(menu, number_of_people)

    total_price = calculate_total_price(menu, number_of_people)
    average_calories = calculate_average_calories(menu)

    print("\nUkesmeny:")
    for day, recipe in menu.items():
        print(f"{day}: {recipe['name']}")

    print("\nHandleliste:")
    for item, amount in shopping_list.items():
        print(f"{item}: {amount:.1f}")

    print(f"\nAnslått totalpris: {total_price:.0f} kr")
    print(f"Snitt kalorier per person per middag: {average_calories:.0f} kcal")


if __name__ == "__main__":
    main()