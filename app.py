import math

import streamlit as st

from src.menu_generator import (
    MENU_PRIORITY_CHEAPEST,
    MENU_PRIORITY_FASTEST,
    MENU_PRIORITY_HEALTHIER,
    MENU_PRIORITY_NONE,
    generate_menu_with_budget
)
from src.products import get_products
from src.shopping_list import (
    group_shopping_list_by_category,
    iter_recipe_ingredients,
    normalize_pantry_items
)

def validate_preferences(preferences, taco_friday):
    errors = []

    if preferences["vegetarian_only"] and preferences.get("exclude_vegetarian"):
        errors.append("Du kan ikke velge både bare vegetarmat og ingen vegetarretter.")

    if preferences["wants_fish"] and "fish" in preferences["excluded_allergens"]:
        errors.append("Du har valgt minst én fiskemiddag, men også valgt å unngå fisk.")

    if taco_friday and preferences["vegetarian_only"]:
        errors.append("Du har valgt taco fredag, men også bare vegetarmat. Vegetartaco er ikke støttet ennå.")

    return errors

def format_amount(amount):
    if amount == int(amount):
        return str(int(amount))
    return f"{amount:.1f}"

def format_package_unit(amount, unit):
    if amount == 1:
        return unit
    if unit =="pakke":
        return "pakker"
    if unit == "boks":
        return "bokser"
    if unit == "pose":
        return "poser"
    if unit == "stk":
        return "stk"
    if unit == "l":
        return "l"
    if unit == "g":
        return "g"
    return unit


def get_product_display_options(products):
    if "products" in products:
        products = products["products"]

    return {
        product.get("display_name", product["name"]): product_key
        for product_key, product in sorted(
            (
                (product_key, product)
                for product_key, product in products.items()
                if isinstance(product, dict)
            ),
            key=lambda item: item[1].get("display_name", item[1]["name"])
        )
    }


def get_pantry_amount_step(product):
    if product["unit"] in {"g", "ml"}:
        return 50.0

    return 1.0


GENERATED_MENU_STATE_KEY = "generated_menu_result"
SHOPPING_CHECKED_STATE_PREFIX = "shopping_item_checked_"
DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]


def get_shopping_item_state_key(product_id):
    return f"{SHOPPING_CHECKED_STATE_PREFIX}{product_id}"


def reset_shopping_item_checkboxes(shopping_list):
    for state_key in list(st.session_state.keys()):
        if state_key.startswith(SHOPPING_CHECKED_STATE_PREFIX):
            del st.session_state[state_key]

    for product_id in shopping_list:
        st.session_state[get_shopping_item_state_key(product_id)] = False


def format_shopping_item_label(item):
    return (
        f"**{item['display_name']}**: "
        f"{format_amount(item['packages_needed'])} {format_package_unit(item['packages_needed'], item['package_unit'])} "
        f"(trenger {format_amount(item['needed_amount'])} {format_package_unit(item['needed_amount'], item['unit'])}) "
        f"- ca. {item['estimated_total_price']} kr"
    )


def get_checked_count(items):
    return sum(
        1
        for item in items
        if st.session_state.get(get_shopping_item_state_key(item["product_id"]), False)
    )


def get_menu_generation_days(menu, taco_friday):
    if taco_friday and "Fredag" in menu:
        return ["Fredag"] + [day for day in DAYS if day != "Fredag"]

    return DAYS


def get_menu_pantry_usage_by_day(menu, pantry_items, products, number_of_people, taco_friday):
    pantry_items = normalize_pantry_items(pantry_items)
    pantry_usage_by_day = {}

    for day in get_menu_generation_days(menu, taco_friday):
        recipe = menu.get(day)

        if recipe is None:
            continue

        base_servings = recipe.get("servings", 4)
        scale_factor = number_of_people / base_servings
        used_product_names = []

        for product_id, amount, _unit in iter_recipe_ingredients(recipe):
            pantry_amount = pantry_items.get(product_id, 0)

            if pantry_amount <= 0:
                continue

            needed_amount = amount * scale_factor
            used_amount = needed_amount

            if not math.isinf(pantry_amount):
                used_amount = min(needed_amount, pantry_amount)

            if used_amount <= 0:
                continue

            product = products.get(product_id, {})
            used_product_names.append(
                product.get("display_name", product.get("name", product_id))
            )

            if not math.isinf(pantry_amount):
                pantry_items[product_id] = max(0, pantry_amount - used_amount)

        pantry_usage_by_day[day] = used_product_names

    return pantry_usage_by_day


def format_pantry_usage(product_names):
    if not product_names:
        return "ingen"

    return ", ".join(product_names)


def format_selected_allergen_status(recipe, excluded_allergens, allergen_display_names):
    excluded_allergens = set(excluded_allergens)

    if not excluded_allergens:
        return "ingen valgt"

    recipe_allergens = set(recipe.get("allergens", []))
    matching_allergens = sorted(recipe_allergens & excluded_allergens)

    if not matching_allergens:
        return "ingen av de valgte"

    return ", ".join(
        allergen_display_names.get(allergen, allergen)
        for allergen in matching_allergens
    )


st.title("MatApp")
st.write("Lag en enkel ukesmeny med handleliste og prisanslag.")

number_of_people = st.number_input(
    "Hvor mange personer skal spise middag?",
    min_value=1,
    max_value=10,
    value=3
)

max_budget = st.number_input(
    "Maksbudsjett for uka",
    min_value=100,
    max_value=3000,
    value=900,
    step=50
)

taco_friday = st.checkbox("Taco på fredag", value=True)
wants_fish = st.checkbox("Minst én fiskemiddag", value=True)
vegetarian_only = st.checkbox("Bare vegetarmat", value=False)
exclude_vegetarian = st.checkbox("Ingen vegetarretter", value=False)

allergen_options = {
    "Gluten / cøliaki": "gluten",
    "Laktose": "lactose",
    "Melk / melkeprotein": "milk",
    "Egg": "egg",
    "Fisk": "fish",
    "Soya": "soy",
    "Nøtter": "nuts"
}
allergen_display_names = {
    allergen: display_name
    for display_name, allergen in allergen_options.items()
}

selected_allergens_display = st.multiselect(
    "Allergener eller matvarer som må unngås",
    options=list(allergen_options.keys())
)

excluded_allergens = [
    allergen_options[name]
    for name in selected_allergens_display
]

max_time_minutes = st.slider(
    "Maks tid per middag",
    min_value=15,
    max_value=90,
    value=40,
    step=5
)

menu_priority_options = {
    "Ingen spesiell prioritering": MENU_PRIORITY_NONE,
    "Billigst mulig": MENU_PRIORITY_CHEAPEST,
    "Raskest mulig": MENU_PRIORITY_FASTEST,
    "Sunnere uke": MENU_PRIORITY_HEALTHIER
}

menu_style = st.selectbox(
    "Hva ønsker du å prioritere?",
    list(menu_priority_options.keys())
)

products = get_products()
if "products" in products:
    products = products["products"]
product_display_options = get_product_display_options(products)

st.subheader("Varer hjemme")
selected_pantry_display_names = st.multiselect(
    "Velg varer du allerede har hjemme",
    options=list(product_display_options.keys())
)

pantry_items = {}

for display_name in selected_pantry_display_names:
    product_key = product_display_options[display_name]
    product = products[product_key]
    amount = st.number_input(
        f"{display_name} hjemme ({product['unit']})",
        min_value=0.0,
        value=float(product["package_size"]),
        step=get_pantry_amount_step(product),
        key=f"pantry_amount_{product_key}"
    )

    if amount > 0:
        pantry_items[product_key] = amount

if pantry_items:
    st.caption(f"{len(pantry_items)} varer blir trukket fra handlelisten.")

preferences = {
    "wants_fish": wants_fish,
    "vegetarian_only": vegetarian_only,
    "exclude_vegetarian": exclude_vegetarian,
    "max_time_minutes": max_time_minutes,
    "avoid_categories": [],
    "excluded_allergens": excluded_allergens,
    "menu_priority": menu_priority_options[menu_style]
}

if taco_friday and vegetarian_only:
    st.warning("Vanlig taco fredag passer ikke med bare vegetarmat ennå.")

if vegetarian_only and exclude_vegetarian:
    st.warning("Velg enten bare vegetarmat eller ingen vegetarretter, ikke begge.")

if wants_fish and "fish" in excluded_allergens:
    st.warning("Du har valgt minst én fiskemiddag, men også valgt å unngå fisk.")

errors = validate_preferences(preferences, taco_friday)

generate_menu = st.button("Generer ukesmeny")

if generate_menu and errors:
    st.session_state.pop(GENERATED_MENU_STATE_KEY, None)

    for error in errors:
        st.warning(error)

if generate_menu and not errors:
    menu, shopping_list, total_price = generate_menu_with_budget(
        number_of_people,
        taco_friday,
        max_budget,
        preferences,
        pantry_items=pantry_items
    )

    if menu is None:
        st.session_state.pop(GENERATED_MENU_STATE_KEY, None)
        st.error("Fant ingen meny som passer budsjettet og preferansene dine.")
    else:
        st.session_state[GENERATED_MENU_STATE_KEY] = {
            "menu": menu,
            "shopping_list": shopping_list,
            "total_price": total_price,
            "pantry_items": pantry_items.copy(),
            "excluded_allergens": excluded_allergens.copy(),
            "number_of_people": number_of_people,
            "taco_friday": taco_friday
        }
        reset_shopping_item_checkboxes(shopping_list)

generated_menu_result = st.session_state.get(GENERATED_MENU_STATE_KEY)

if generated_menu_result is not None:
    menu = generated_menu_result["menu"]
    shopping_list = generated_menu_result["shopping_list"]
    total_price = generated_menu_result["total_price"]
    generated_pantry_items = generated_menu_result.get("pantry_items", {})
    generated_excluded_allergens = generated_menu_result.get("excluded_allergens", [])
    generated_number_of_people = generated_menu_result.get(
        "number_of_people",
        number_of_people
    )
    generated_taco_friday = generated_menu_result.get("taco_friday", taco_friday)
    pantry_usage_by_day = get_menu_pantry_usage_by_day(
        menu,
        generated_pantry_items,
        products,
        generated_number_of_people,
        generated_taco_friday
    )

    st.subheader("Ukesmeny")

    for day in DAYS:
        if day in menu:
            recipe = menu[day]
            with st.expander(f"**{day}:** {recipe['name']}"):
                st.write(f"Tid: {recipe['time_minutes']} minutter")
                st.write(
                    "Bruker varer du har hjemme: "
                    f"{format_pantry_usage(pantry_usage_by_day.get(day, []))}"
                )
                st.write(
                    "Allergener: "
                    f"{format_selected_allergen_status(recipe, generated_excluded_allergens, allergen_display_names)}"
                )
                st.write(f"Vanskelighetsgrad: {recipe['difficulty']}")
                st.write(f"Tags: {', '.join(recipe.get('tags', []))}")

    st.subheader("Handleliste")

    if not shopping_list:
        st.info("Du har allerede alle varene som trengs til denne menyen.")
    else:
        checked_items_total = 0

        for category, items in group_shopping_list_by_category(shopping_list):
            checked_items = get_checked_count(items)
            checked_items_total += checked_items
            category_is_complete = checked_items == len(items)

            if category_is_complete:
                st.markdown(f"#### {category} - ferdig ({checked_items}/{len(items)})")
            else:
                st.markdown(f"#### {category} ({checked_items}/{len(items)})")

            for item in items:
                st.checkbox(
                    format_shopping_item_label(item),
                    key=get_shopping_item_state_key(item["product_id"])
                )

        if checked_items_total == len(shopping_list):
            st.success("Alt er handlet.")

    st.subheader("Pris")
    st.success(f"Anslått handlepris: {total_price:.0f} kr")
    st.caption("Prisen er basert på avrundede butikkpakker, ikke nøyaktig forbrukt mengde.")
