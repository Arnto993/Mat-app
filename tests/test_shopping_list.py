from src.shopping_list import create_raw_shopping_list
from src.shopping_list import create_rounded_shopping_list
from src.shopping_list import group_shopping_list_by_category


def test_create_raw_shopping_list_scales_with_number_of_people():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 400, "unit": "g"},
                {"product_id": "ground_beef_400", "amount": 600, "unit": "g"}
            ]
        }
    }

    shopping_list = create_raw_shopping_list(menu, number_of_people=2)

    assert shopping_list["rice_jasmin_1000"] == 200
    assert shopping_list["ground_beef_400"] == 300

def test_create_raw_shopping_list_combines_same_ingredients():
    menu = {
        "Mandag": {
            "name": "Rett 1",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 400, "unit": "g"}
            ]
        },
        "Tirsdag": {
            "name": "Rett 2",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 300, "unit": "g"}
            ]
        }
    }

    shopping_list = create_raw_shopping_list(menu, number_of_people=4)

    assert shopping_list["rice_jasmin_1000"] == 700


def test_create_raw_shopping_list_skips_pantry_items():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 400, "unit": "g"},
                {"product_id": "ground_beef_400", "amount": 600, "unit": "g"}
            ]
        }
    }

    shopping_list = create_raw_shopping_list(
        menu,
        number_of_people=4,
        pantry_items={"rice_jasmin_1000"}
    )

    assert "rice_jasmin_1000" not in shopping_list
    assert shopping_list["ground_beef_400"] == 600


def test_create_raw_shopping_list_subtracts_pantry_amounts():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 1200, "unit": "g"},
                {"product_id": "ground_beef_400", "amount": 600, "unit": "g"}
            ]
        }
    }

    shopping_list = create_raw_shopping_list(
        menu,
        number_of_people=4,
        pantry_items={"rice_jasmin_1000": 500}
    )

    assert shopping_list["rice_jasmin_1000"] == 700
    assert shopping_list["ground_beef_400"] == 600


def test_create_rounded_shopping_list_rounds_up_packages():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 1200, "unit": "g"}
            ]
        }
    }

    shopping_list = create_rounded_shopping_list(menu, number_of_people=4)

    assert shopping_list["rice_jasmin_1000"]["packages_needed"] == 2


def test_create_rounded_shopping_list_skips_pantry_items():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 1200, "unit": "g"},
                {"product_id": "ground_beef_400", "amount": 600, "unit": "g"}
            ]
        }
    }

    shopping_list = create_rounded_shopping_list(
        menu,
        number_of_people=4,
        pantry_items={"rice_jasmin_1000"}
    )

    assert "rice_jasmin_1000" not in shopping_list
    assert "ground_beef_400" in shopping_list


def test_create_rounded_shopping_list_rounds_after_subtracting_pantry_amounts():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 1200, "unit": "g"}
            ]
        }
    }

    shopping_list = create_rounded_shopping_list(
        menu,
        number_of_people=4,
        pantry_items={"rice_jasmin_1000": 500}
    )

    assert shopping_list["rice_jasmin_1000"]["needed_amount"] == 700
    assert shopping_list["rice_jasmin_1000"]["packages_needed"] == 1


def test_create_rounded_shopping_list_prorates_pantry_cost_mode():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rapeseed_oil_1000", "amount": 100, "unit": "ml"}
            ]
        }
    }

    shopping_list = create_rounded_shopping_list(menu, number_of_people=4)

    assert shopping_list["rapeseed_oil_1000"]["packages_needed"] == 0.1
    assert shopping_list["rapeseed_oil_1000"]["estimated_total_price"] == 3.99


def test_create_rounded_shopping_list_sorts_by_norwegian_store_order():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 400, "unit": "g"},
                {"product_id": "frozen_peas_600", "amount": 300, "unit": "g"},
                {"product_id": "ground_beef_400", "amount": 400, "unit": "g"},
                {"product_id": "broccoli_400", "amount": 400, "unit": "g"},
                {"product_id": "chopped_tomatoes_400", "amount": 400, "unit": "g"},
                {"product_id": "milk_1000", "amount": 1000, "unit": "ml"}
            ]
        }
    }

    shopping_list = create_rounded_shopping_list(menu, number_of_people=4)

    assert list(shopping_list.keys()) == [
        "broccoli_400",
        "ground_beef_400",
        "milk_1000",
        "rice_jasmin_1000",
        "chopped_tomatoes_400",
        "frozen_peas_600"
    ]


def test_group_shopping_list_by_category_uses_headings_and_frozen_category():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": [
                {"product_id": "frozen_peas_600", "amount": 300, "unit": "g"},
                {"product_id": "broccoli_400", "amount": 400, "unit": "g"},
                {"product_id": "rice_jasmin_1000", "amount": 400, "unit": "g"}
            ]
        }
    }

    shopping_list = create_rounded_shopping_list(menu, number_of_people=4)
    grouped_list = group_shopping_list_by_category(shopping_list)

    assert [category for category, _items in grouped_list] == [
        "Frukt og grønt",
        "Tørrvarer",
        "Frysevarer"
    ]
    assert grouped_list[-1][1][0]["display_name"] == "Erter fryst"
