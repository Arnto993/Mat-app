import streamlit as st

from src.menu_generator import (
    MENU_PRIORITY_CHEAPEST,
    MENU_PRIORITY_FASTEST,
    MENU_PRIORITY_HEALTHIER,
    MENU_PRIORITY_NONE,
    generate_menu_with_budget
)
from src.products import get_products
from src.shopping_list import group_shopping_list_by_category

def validate_preferences(preferences, taco_friday):
    errors = []

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

allergen_options = {
    "Gluten / cøliaki": "gluten",
    "Laktose": "lactose",
    "Melk / melkeprotein": "milk",
    "Egg": "egg",
    "Fisk": "fish",
    "Soya": "soy",
    "Nøtter": "nuts"
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
    "max_time_minutes": max_time_minutes,
    "avoid_categories": [],
    "excluded_allergens": excluded_allergens,
    "menu_priority": menu_priority_options[menu_style]
}

if taco_friday and vegetarian_only:
    st.warning("Vanlig taco fredag passer ikke med bare vegetarmat ennå.")

if wants_fish and "fish" in excluded_allergens:
    st.warning("Du har valgt minst én fiskemiddag, men også valgt å unngå fisk.")

errors = validate_preferences(preferences, taco_friday)

generate_menu = st.button("Generer ukesmeny")

if generate_menu and errors:
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
        st.error("Fant ingen meny som passer budsjettet og preferansene dine.")
    else:
        st.subheader("Ukesmeny")

        DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]

        for day in DAYS:
            if day in menu:
                recipe = menu[day]
                with st.expander(f"**{day}:** {recipe['name']}"):
                    st.write(f"Tid: {recipe['time_minutes']} minutter")
                    st.write(f"Vanskelighetsgrad: {recipe['difficulty']}")
                    st.write(f"Tags: {', '.join(recipe.get('tags', []))}")

        st.subheader("Handleliste")

        if not shopping_list:
            st.info("Du har allerede alle varene som trengs til denne menyen.")
        else:
            for category, items in group_shopping_list_by_category(shopping_list):
                st.markdown(f"#### {category}")

                for item in items:
                    st.write(
                        f"- **{item['display_name']}**: "
                        f"{format_amount(item['packages_needed'])} {format_package_unit(item['packages_needed'], item['package_unit'])} "
                        f"(trenger {format_amount(item['needed_amount'])} {format_package_unit(item['needed_amount'], item['unit'])}) "
                        f"– ca. {item['estimated_total_price']} kr"
                    )

        st.subheader("Pris")
        st.success(f"Anslått handlepris: {total_price:.0f} kr")
        st.caption("Prisen er basert på avrundede butikkpakker, ikke nøyaktig forbrukt mengde.")
