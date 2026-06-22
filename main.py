from menu_generator import generate_week_menu
from shopping_list import create_rounded_shopping_list


def calculate_total_price_from_shopping_list(shopping_list):
    total_price = 0

    for item in shopping_list.values():
        total_price += item["estimated_total_price"]

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
    shopping_list = create_rounded_shopping_list(menu, number_of_people)

    total_price = calculate_total_price_from_shopping_list(shopping_list)
    average_calories = calculate_average_calories(menu)

    print("\nUkesmeny:")
    for day, recipe in menu.items():
        print(f"{day}: {recipe['name']}")

    print("\nHandleliste:")
    for item in shopping_list.values():
        print(
            f"{item['display_name']}: "
            f"{item['packages_needed']} {item['package_unit']} "
            f"(trenger {item['needed_amount']:.1f} {item['unit']}) "
            f"- ca. {item['estimated_total_price']} kr"
        )

    print(f"\nAnslått totalpris: {total_price:.0f} kr")
    print(f"Snitt kalorier per person per middag: {average_calories:.0f} kcal")


if __name__ == "__main__":
    main()