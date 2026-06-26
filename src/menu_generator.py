import random

from src.products import get_products
from src.recipes import get_recipes
from src.shopping_list import create_rounded_shopping_list, iter_recipe_ingredients
from src.price_calculator import calculate_total_price_from_shopping_list
from src.allergens import recipe_has_excluded_allergens


DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]
MENU_PRIORITY_NONE = None
MENU_PRIORITY_CHEAPEST = "cheapest"
MENU_PRIORITY_FASTEST = "fastest"
MENU_PRIORITY_HEALTHIER = "healthier"
PRIORITIZED_POOL_MIN_EXTRA = 3
PRIORITIZED_POOL_SHARE = 0.4


def normalize_recipes(recipes):
    if isinstance(recipes, dict):
        recipes = recipes.get("recipes", [])

    return [
        recipe
        for recipe in recipes
        if isinstance(recipe, dict)
    ]


def get_menu_priority(preferences):
    priority = preferences.get("menu_priority")

    if priority in {
        MENU_PRIORITY_CHEAPEST,
        MENU_PRIORITY_FASTEST,
        MENU_PRIORITY_HEALTHIER
    }:
        return priority

    return MENU_PRIORITY_NONE


def find_recipe_by_name(recipes, name):
    recipes = normalize_recipes(recipes)

    for recipe in recipes:
        if recipe["name"].lower() == name.lower():
            return recipe

    return None


def find_taco_recipe(recipes):
    recipes = normalize_recipes(recipes)
    exact_match = find_recipe_by_name(recipes, "Taco")

    if exact_match is not None:
        return exact_match

    for recipe in recipes:
        recipe_id = recipe.get("id", "").lower()
        recipe_name = recipe.get("name", "").lower()

        if "taco" in recipe_id or "taco" in recipe_name:
            return recipe

    return None


def get_recipe_ingredient_ids(recipe):
    return [
        product_id
        for product_id, _amount, _unit in iter_recipe_ingredients(recipe)
    ]


def get_recipe_product_categories(recipe):
    products = get_products()
    categories = set()

    for product_id in get_recipe_ingredient_ids(recipe):
        product = products.get(product_id)

        if product is not None:
            categories.add(product.get("category"))

    return categories


def recipe_contains_fish(recipe):
    tags = get_recipe_tags(recipe)

    return (
        recipe.get("contains_fish", False)
        or recipe.get("category") == "fisk"
        or "fish" in recipe.get("allergens", [])
        or "fisk" in tags
        or "Fisk" in get_recipe_product_categories(recipe)
    )


def recipe_is_vegetarian(recipe):
    tags = get_recipe_tags(recipe)

    if recipe.get("vegetarian") is not None:
        return recipe["vegetarian"]

    if "vegetar" in tags:
        return True

    non_vegetarian_tags = {"kjøtt", "kylling", "fisk"}
    non_vegetarian_categories = {"Kjøtt", "Fisk"}

    return (
        tags.isdisjoint(non_vegetarian_tags)
        and get_recipe_product_categories(recipe).isdisjoint(non_vegetarian_categories)
    )



def has_fish(menu):
    return any(
        recipe_contains_fish(recipe)
        for recipe in menu.values()
    )


def calculate_menu_time(menu):
    return sum(
        recipe.get("time_minutes", 999)
        for recipe in menu.values()
    )


def calculate_menu_health_score(menu):
    if not menu:
        return 0

    return sum(
        recipe.get("healthy_score", 0)
        for recipe in menu.values()
    ) / len(menu)


def calculate_menu_calories(menu):
    return sum(
        recipe.get("calories_per_portion", 0)
        for recipe in menu.values()
    )


def estimate_recipe_price(recipe):
    if "estimated_price" in recipe:
        return recipe["estimated_price"]

    products = get_products()
    total_price = 0

    for product_id, amount, _unit in iter_recipe_ingredients(recipe):
        product = products.get(product_id)

        if product is None:
            continue

        total_price += amount / product["package_size"] * product["price_nok"]

    return total_price


def calculate_menu_recipe_price(menu):
    return sum(
        estimate_recipe_price(recipe)
        for recipe in menu.values()
    )


def get_recipe_tags(recipe):
    return {
        tag.lower()
        for tag in recipe.get("tags", [])
    }


def get_recipe_priority_score(recipe, priority):
    tags = get_recipe_tags(recipe)

    if priority == MENU_PRIORITY_CHEAPEST:
        score = -estimate_recipe_price(recipe)

        if "billig" in tags:
            score += 25
        if "student" in tags:
            score += 5

        return score

    if priority == MENU_PRIORITY_FASTEST:
        score = -recipe.get("time_minutes", 999)

        if "rask" in tags:
            score += 10
        if "enkel" in tags or "lett" in tags:
            score += 4

        return score

    if priority == MENU_PRIORITY_HEALTHIER:
        score = recipe.get("healthy_score", 0) * 100

        if "calories_per_portion" in recipe:
            score -= recipe["calories_per_portion"] / 20

        if "sunn" in tags or "sunnere" in tags:
            score += 25
        if "vegetar" in tags:
            score += 10
        if "fisk" in tags:
            score += 8
        if "protein" in tags:
            score += 8

        return score

    return 0


def get_prioritized_recipe_pool(recipes, priority, count):
    recipes = normalize_recipes(recipes)

    if priority is MENU_PRIORITY_NONE:
        return recipes.copy()

    sorted_recipes = sorted(
        recipes,
        key=lambda recipe: get_recipe_priority_score(recipe, priority),
        reverse=True
    )
    pool_size = max(
        count + PRIORITIZED_POOL_MIN_EXTRA,
        int(len(sorted_recipes) * PRIORITIZED_POOL_SHARE)
    )

    return sorted_recipes[:min(len(sorted_recipes), pool_size)]


def weighted_sample_without_replacement(recipes, count):
    selected_recipes = []
    available_recipes = normalize_recipes(recipes).copy()

    for _ in range(count):
        weights = list(range(len(available_recipes), 0, -1))
        selected_recipe = random.choices(available_recipes, weights=weights, k=1)[0]

        selected_recipes.append(selected_recipe)
        available_recipes.remove(selected_recipe)

    return selected_recipes


def select_recipes_for_menu(recipes, count, priority):
    recipes = normalize_recipes(recipes)

    if len(recipes) < count:
        return None

    if priority is MENU_PRIORITY_NONE:
        return random.sample(recipes, count)

    recipe_pool = get_prioritized_recipe_pool(recipes, priority, count)

    if len(recipe_pool) < count:
        return None

    return weighted_sample_without_replacement(recipe_pool, count)


def filter_recipes(recipes, preferences):
    filtered_recipes = []
    recipes = normalize_recipes(recipes)

    for recipe in recipes:
        if preferences.get("wants_fish") is False and recipe_contains_fish(recipe):
            continue

        if preferences.get("vegetarian_only") and not recipe_is_vegetarian(recipe):
            continue

        max_time = preferences.get("max_time_minutes")
        if max_time is not None and recipe.get("time_minutes", 999) > max_time:
            continue

        avoid_categories = preferences.get("avoid_categories", [])
        if (
            recipe.get("category") in avoid_categories
            or not get_recipe_product_categories(recipe).isdisjoint(avoid_categories)
        ):
            continue

        excluded_allergens = preferences.get("excluded_allergens", [])
        if recipe_has_excluded_allergens(recipe, excluded_allergens):
            continue

        filtered_recipes.append(recipe)

    return filtered_recipes


def menu_matches_preferences(menu, preferences):
    # Hvis brukeren vil ha fisk, må menyen inneholde minst én fiskerett
    if preferences.get("wants_fish") is True and not has_fish(menu):
        return False

    # Hvis brukeren ikke vil ha fisk, skal menyen ikke ha fisk
    if preferences.get("wants_fish") is False and has_fish(menu):
        return False

    return True


def generate_week_menu(recipes, taco_friday=True, priority=MENU_PRIORITY_NONE):
    menu = {}
    available_recipes = normalize_recipes(recipes).copy()

    if taco_friday:
        taco = find_taco_recipe(available_recipes)

        if taco is None:
            return None

        menu["Fredag"] = taco
        available_recipes.remove(taco)

    days_to_fill = [day for day in DAYS if day not in menu]

    if len(available_recipes) < len(days_to_fill):
        return None

    selected_recipes = select_recipes_for_menu(
        available_recipes,
        len(days_to_fill),
        priority
    )

    if selected_recipes is None:
        return None

    for day, recipe in zip(days_to_fill, selected_recipes):
        menu[day] = recipe

    return menu


def generate_menu_with_budget(
    number_of_people,
    taco_friday,
    max_budget,
    preferences,
    max_attempts=100,
    pantry_items=None
):
    recipes = normalize_recipes(get_recipes())
    available_recipes = filter_recipes(recipes, preferences)
    menu_priority = get_menu_priority(preferences)

    for attempt in range(max_attempts):
        menu = generate_week_menu(available_recipes, taco_friday, menu_priority)

        if menu is None:
            return None, None, None

        if not menu_matches_preferences(menu, preferences):
            continue

        shopping_list = create_rounded_shopping_list(
            menu,
            number_of_people,
            pantry_items
        )
        total_price = calculate_total_price_from_shopping_list(shopping_list)

        if total_price <= max_budget:
            return menu, shopping_list, total_price

    return None, None, None
