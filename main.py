from menu_generator import generate_week_menu
from shopping_list import create_shopping_list

def main():
    number_of_people = int(input("Hvor mange personer? "))
    budget = int(input("Hva er budsjettet for uka? "))
    taco_friday = input("Vil du ha taco på fredag? ja/nei: ").lower() == "ja"

    menu = generate_week_menu(number_of_people, taco_friday)
    shopping_list = create_shopping_list(menu)

    print("\nUkesmeny:")
    for day, recipe in menu.items():
        print(f"{day}: {recipe['name']}")

    print("\nHandleliste:")
    for item, amount in shopping_list.items():
        print(f"{item}: {amount}")

if __name__ == "__main__":
    main()