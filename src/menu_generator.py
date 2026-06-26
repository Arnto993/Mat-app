import math
import random

from src.products import get_products
from src.recipes import get_recipes
from src.shopping_list import (
    create_rounded_shopping_list,
    iter_recipe_ingredients,
    normalize_pantry_items
)
from src.price_calculator import calculate_total_price_from_shopping_list
from src.allergens import recipe_has_excluded_allergens


DAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]
MENU_PRIORITY_NONE = None
MENU_PRIORITY_CHEAPEST = "cheapest"
MENU_PRIORITY_FASTEST = "fastest"
MENU_PRIORITY_HEALTHIER = "healthier"
PRIORITIZED_POOL_MIN_EXTRA = 3
PRIORITIZED_POOL_SHARE = 0.4
PANTRY_MATCH_SCORE = 25
PANTRY_USED_SHARE_SCORE = 10


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


def has_vegetarian(menu):
    return any(
        recipe_is_vegetarian(recipe)
        for recipe in menu.values()
    )


def get_recipe_identity(recipe):
    return recipe.get("id", recipe.get("name", "")).lower()


def get_adjacent_days(day):
    if day not in DAYS:
        return []

    day_index = DAYS.index(day)
    adjacent_days = []

    if day_index > 0:
        adjacent_days.append(DAYS[day_index - 1])

    if day_index < len(DAYS) - 1:
        adjacent_days.append(DAYS[day_index + 1])

    return adjacent_days


def get_adjacent_recipes(menu, day):
    return [
        menu[adjacent_day]
        for adjacent_day in get_adjacent_days(day)
        if adjacent_day in menu
    ]


def replacement_has_fish_conflict(recipe, menu, day):
    return (
        recipe_contains_fish(recipe)
        and any(
            recipe_contains_fish(adjacent_recipe)
            for adjacent_recipe in get_adjacent_recipes(menu, day)
        )
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


def get_product_unit_price(product):
    package_size = product.get("package_size", 0)

    if package_size <= 0:
        return 0

    price = product.get("price_nok", product.get("estimated_package_price", 0))

    return price / package_size


def get_recipe_pantry_usage_score(recipe, pantry_items=None, number_of_people=1):
    pantry_items = normalize_pantry_items(pantry_items)

    if not pantry_items or "ingredients" not in recipe:
        return 0

    products = get_products()
    base_servings = recipe.get("servings", 4)
    scale_factor = number_of_people / base_servings
    score = 0

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
        score += PANTRY_MATCH_SCORE
        score += used_amount * get_product_unit_price(product)

        if not math.isinf(pantry_amount):
            score += min(used_amount / pantry_amount, 1) * PANTRY_USED_SHARE_SCORE

    return score


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


def get_recipe_selection_score(
    recipe,
    priority,
    pantry_items=None,
    number_of_people=1
):
    return (
        get_recipe_priority_score(recipe, priority)
        + get_recipe_pantry_usage_score(recipe, pantry_items, number_of_people)
    )


def get_prioritized_recipe_pool(
    recipes,
    priority,
    count,
    pantry_items=None,
    number_of_people=1
):
    recipes = normalize_recipes(recipes)
    pantry_items = normalize_pantry_items(pantry_items)

    if priority is MENU_PRIORITY_NONE and not pantry_items:
        return recipes.copy()

    sorted_recipes = sorted(
        recipes,
        key=lambda recipe: get_recipe_selection_score(
            recipe,
            priority,
            pantry_items,
            number_of_people
        ),
        reverse=True
    )
    pool_size = max(
        count + PRIORITIZED_POOL_MIN_EXTRA,
        int(len(sorted_recipes) * PRIORITIZED_POOL_SHARE)
    )

    return sorted_recipes[:min(len(sorted_recipes), pool_size)]


def remove_recipe_ingredients_from_pantry(recipe, pantry_items, number_of_people=1):
    base_servings = recipe.get("servings", 4)
    scale_factor = number_of_people / base_servings

    for product_id, amount, _unit in iter_recipe_ingredients(recipe):
        if product_id not in pantry_items or math.isinf(pantry_items[product_id]):
            continue

        pantry_items[product_id] = max(
            0,
            pantry_items[product_id] - amount * scale_factor
        )


def weighted_sample_without_replacement(
    recipes,
    count,
    priority=MENU_PRIORITY_NONE,
    pantry_items=None,
    number_of_people=1
):
    selected_recipes = []
    available_recipes = normalize_recipes(recipes).copy()
    pantry_items = normalize_pantry_items(pantry_items)

    for _ in range(count):
        if pantry_items:
            available_recipes = sorted(
                available_recipes,
                key=lambda recipe: get_recipe_selection_score(
                    recipe,
                    priority,
                    pantry_items,
                    number_of_people
                ),
                reverse=True
            )

        weights = list(range(len(available_recipes), 0, -1))
        selected_recipe = random.choices(available_recipes, weights=weights, k=1)[0]

        selected_recipes.append(selected_recipe)
        available_recipes.remove(selected_recipe)
        remove_recipe_ingredients_from_pantry(
            selected_recipe,
            pantry_items,
            number_of_people
        )

    return selected_recipes


def select_recipes_for_menu(
    recipes,
    count,
    priority,
    pantry_items=None,
    number_of_people=1
):
    recipes = normalize_recipes(recipes)
    pantry_items = normalize_pantry_items(pantry_items)

    if len(recipes) < count:
        return None

    if priority is MENU_PRIORITY_NONE and not pantry_items:
        return random.sample(recipes, count)

    recipe_pool = get_prioritized_recipe_pool(
        recipes,
        priority,
        count,
        pantry_items,
        number_of_people
    )

    if len(recipe_pool) < count:
        return None

    return weighted_sample_without_replacement(
        recipe_pool,
        count,
        priority,
        pantry_items,
        number_of_people
    )


def get_replacement_context_score(recipe, menu, day):
    score = 0
    recipe_category = recipe.get("category")
    recipe_tags = get_recipe_tags(recipe)

    for adjacent_recipe in get_adjacent_recipes(menu, day):
        adjacent_category = adjacent_recipe.get("category")
        adjacent_tags = get_recipe_tags(adjacent_recipe)

        if recipe_category and recipe_category == adjacent_category:
            score -= 20

        shared_tags = recipe_tags & adjacent_tags
        shared_tags -= {"hverdagsmiddag", "rask", "enkel", "billig", "student"}
        score -= len(shared_tags) * 4

        if recipe_is_vegetarian(recipe) == recipe_is_vegetarian(adjacent_recipe):
            score -= 3

    return score


def get_replacement_recipe_candidates(recipes, menu, day, preferences):
    recipes = normalize_recipes(recipes)
    menu_without_day = {
        menu_day: recipe
        for menu_day, recipe in menu.items()
        if menu_day != day
    }
    used_recipe_identities = {
        get_recipe_identity(recipe)
        for recipe in menu.values()
    }
    candidates = []

    for recipe in filter_recipes(recipes, preferences):
        if get_recipe_identity(recipe) in used_recipe_identities:
            continue

        if replacement_has_fish_conflict(recipe, menu_without_day, day):
            continue

        if preferences.get("wants_fish") is True:
            menu_needs_fish_replacement = not has_fish(menu_without_day)

            if menu_needs_fish_replacement and not recipe_contains_fish(recipe):
                continue

        candidates.append(recipe)

    return candidates


def select_replacement_recipe(
    recipes,
    menu,
    day,
    priority,
    pantry_items=None,
    number_of_people=1
):
    recipes = normalize_recipes(recipes)
    pantry_items = normalize_pantry_items(pantry_items)

    if not recipes:
        return None

    ranked_recipes = sorted(
        recipes,
        key=lambda recipe: (
            get_recipe_selection_score(
                recipe,
                priority,
                pantry_items,
                number_of_people
            )
            + get_replacement_context_score(recipe, menu, day)
        ),
        reverse=True
    )
    weights = list(range(len(ranked_recipes), 0, -1))

    return random.choices(ranked_recipes, weights=weights, k=1)[0]


def filter_recipes(recipes, preferences):
    filtered_recipes = []
    recipes = normalize_recipes(recipes)

    for recipe in recipes:
        if preferences.get("wants_fish") is False and recipe_contains_fish(recipe):
            continue

        if preferences.get("vegetarian_only") and not recipe_is_vegetarian(recipe):
            continue

        if preferences.get("exclude_vegetarian") and recipe_is_vegetarian(recipe):
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

    if preferences.get("vegetarian_only") and not all(
        recipe_is_vegetarian(recipe)
        for recipe in menu.values()
    ):
        return False

    if preferences.get("exclude_vegetarian") and has_vegetarian(menu):
        return False

    return True


def generate_week_menu(
    recipes,
    taco_friday=True,
    priority=MENU_PRIORITY_NONE,
    pantry_items=None,
    number_of_people=1
):
    menu = {}
    available_recipes = normalize_recipes(recipes).copy()
    pantry_items = normalize_pantry_items(pantry_items)

    if taco_friday:
        taco = find_taco_recipe(available_recipes)

        if taco is None:
            return None

        menu["Fredag"] = taco
        available_recipes.remove(taco)
        remove_recipe_ingredients_from_pantry(taco, pantry_items, number_of_people)

    days_to_fill = [day for day in DAYS if day not in menu]

    if len(available_recipes) < len(days_to_fill):
        return None

    selected_recipes = select_recipes_for_menu(
        available_recipes,
        len(days_to_fill),
        priority,
        pantry_items,
        number_of_people
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
        menu = generate_week_menu(
            available_recipes,
            taco_friday,
            menu_priority,
            pantry_items,
            number_of_people
        )

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


def replace_menu_day_with_budget(
    menu,
    day,
    number_of_people,
    max_budget,
    preferences,
    max_attempts=100,
    pantry_items=None
):
    recipes = normalize_recipes(get_recipes())
    candidates = get_replacement_recipe_candidates(
        recipes,
        menu,
        day,
        preferences
    )
    menu_priority = get_menu_priority(preferences)

    for _attempt in range(max_attempts):
        replacement_recipe = select_replacement_recipe(
            candidates,
            menu,
            day,
            menu_priority,
            pantry_items,
            number_of_people
        )

        if replacement_recipe is None:
            return None, None, None

        new_menu = menu.copy()
        new_menu[day] = replacement_recipe

        if not menu_matches_preferences(new_menu, preferences):
            candidates.remove(replacement_recipe)
            continue

        shopping_list = create_rounded_shopping_list(
            new_menu,
            number_of_people,
            pantry_items
        )
        total_price = calculate_total_price_from_shopping_list(shopping_list)

        if total_price <= max_budget:
            return new_menu, shopping_list, total_price

        candidates.remove(replacement_recipe)

    return None, None, None
