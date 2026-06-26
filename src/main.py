from src.menu_generator import generate_menu_with_budget
from src.shopping_list import group_shopping_list_by_category


def format_amount(amount):
    if amount == int(amount):
        return str(int(amount))
    return f"{amount:.1f}"


def calculate_average_calories(menu):
    recipes_with_calories = [
        recipe
        for recipe in menu.values()
        if "calories_per_portion" in recipe
    ]

    if not recipes_with_calories:
        return None

    total_calories = 0

    for recipe in recipes_with_calories:
        total_calories += recipe["calories_per_portion"]

    return total_calories / len(recipes_with_calories)


def main():
    number_of_people = int(input("Hvor mange personer skal spise middag? "))

    max_budget = int(input("Hva er maks budsjett for uken? (i kr): "))

    taco_friday = input("Vil du ha taco på fredag? ja/nei: ").lower() == "ja"
    wants_fish = input("Vil du ha fisk i ukesmenyen? ja/nei: ").lower() == "ja"
    max_time_minutes = int(input("Hva er maks tid du vil bruke på middag? (i minutter): "))
    vegetarian_only = input("Vil du ha kun vegetariske retter? ja/nei: ").lower() == "ja"
    exclude_vegetarian = input("Vil du unngå vegetariske retter helt? ja/nei: ").lower() == "ja"

    preferences = {
        "wants_fish": wants_fish,
        "vegetarian_only": vegetarian_only,
        "exclude_vegetarian": exclude_vegetarian,
        "max_time_minutes": max_time_minutes,
        "avoid_categories": []
    }

    if vegetarian_only and exclude_vegetarian:
        print("Du kan ikke velge både bare vegetarmat og ingen vegetarretter.")
        return

    if taco_friday and vegetarian_only:
        print("Vanlig taco fredag passer ikke med bare vegetarmat ennå.")

    menu, shopping_list, total_price = generate_menu_with_budget(
        number_of_people,
        taco_friday,
        max_budget,
        preferences
    )

    if menu is None:
        print("Kunne ikke generere en ukesmeny innenfor budsjettet og preferansene.")
        return
    
    average_calories = calculate_average_calories(menu)

    print("\nUkesmeny:")
    for day, recipe in menu.items():
        print(f"{day}: {recipe['name']}")

    print("\nHandleliste:")
    for category, items in group_shopping_list_by_category(shopping_list):
        print(f"\n{category}:")

        for item in items:
            print(
                f"- {item['display_name']}: "
                f"{format_amount(item['packages_needed'])} {item['package_unit']} "
                f"(trenger {item['needed_amount']:.1f} {item['unit']}) "
                f"- ca. {item['estimated_total_price']} kr"
            )

    print(f"\nAnslått totalpris: {total_price:.0f} kr")
    if average_calories is not None:
        print(f"Snitt kalorier per person per middag: {average_calories:.0f} kcal")


if __name__ == "__main__":
    main()
