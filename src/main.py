from src.menu_generator import generate_menu_with_budget


def calculate_average_calories(menu):
    total_calories = 0

    for recipe in menu.values():
        total_calories += recipe["calories_per_portion"]

    return total_calories / len(menu)


def main():
    number_of_people = int(input("Hvor mange personer skal spise middag? "))

    max_budget = int(input("Hva er maks budsjett for uken? (i kr): "))

    taco_friday = input("Vil du ha taco på fredag? ja/nei: ").lower() == "ja"
    wants_fish = input("Vil du ha fisk i ukesmenyen? ja/nei: ").lower() == "ja"
    max_time_minutes = int(input("Hva er maks tid du vil bruke på middag? (i minutter): "))
    vegetarian_only = input("Vil du ha kun vegetariske retter? ja/nei: ").lower() == "ja"

    preferences = {
        "wants_fish": wants_fish,
        "vegetarian_only": vegetarian_only,
        "max_time_minutes": max_time_minutes,
        "avoid_categories": []
    }

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