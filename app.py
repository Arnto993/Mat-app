import streamlit as st

from src.menu_generator import generate_menu_with_budget


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

preferences = {
    "wants_fish": wants_fish,
    "vegetarian_only": vegetarian_only,
    "max_time_minutes": max_time_minutes,
    "avoid_categories": [],
    "excluded_allergens": excluded_allergens
}

if taco_friday and vegetarian_only:
    st.warning("Vanlig taco fredag passer ikke med bare vegetarmat ennå.")

if wants_fish and "fish" in excluded_allergens:
    st.warning("Du har valgt minst én fiskemiddag, men også valgt å unngå fisk.")

if st.button("Generer ukesmeny"):
    menu, shopping_list, total_price = generate_menu_with_budget(
        number_of_people,
        taco_friday,
        max_budget,
        preferences
    )

    if menu is None:
        st.error("Fant ingen meny som passer budsjettet og preferansene dine.")
    else:
        st.subheader("Ukesmeny")

        DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]

        for day in DAYS:
            if day in menu:
                recipe = menu[day]
                st.write(f"**{day}:** {recipe['name']}")

        st.subheader("Handleliste")

        for item in shopping_list.values():
            st.write(
                f"- **{item['display_name']}**: "
                f"{item['packages_needed']} {format_package_unit(item['packages_needed'], item['package_unit'])} "
                f"(trenger {format_amount(item['needed_amount'])} {format_package_unit(item['needed_amount'], item['unit'])}) "
                f"– ca. {item['estimated_total_price']} kr"
            )

        st.subheader("Pris")
        st.success(f"Anslått handlepris: {total_price:.0f} kr")
        st.caption("Prisen er basert på avrundede butikkpakker, ikke nøyaktig forbrukt mengde.")