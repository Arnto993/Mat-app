from src.shopping_list import create_raw_shopping_list
from src.shopping_list import create_rounded_shopping_list


def test_create_raw_shopping_list_scales_with_number_of_people():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": {
                "ris": 400,
                "kjottdeig": 600
            }
        }
    }

    shopping_list = create_raw_shopping_list(menu, number_of_people=2)

    assert shopping_list["ris"] == 200
    assert shopping_list["kjottdeig"] == 300

def test_create_raw_shopping_list_combines_same_ingredients():
    menu = {
        "Mandag": {
            "name": "Rett 1",
            "servings": 4,
            "ingredients": {
                "ris": 400
            }
        },
        "Tirsdag": {
            "name": "Rett 2",
            "servings": 4,
            "ingredients": {
                "ris": 300
            }
        }
    }

    shopping_list = create_raw_shopping_list(menu, number_of_people=4)

    assert shopping_list["ris"] == 700


def test_create_raw_shopping_list_skips_pantry_items():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": {
                "ris": 400,
                "kjottdeig": 600
            }
        }
    }

    shopping_list = create_raw_shopping_list(
        menu,
        number_of_people=4,
        pantry_items={"ris"}
    )

    assert "ris" not in shopping_list
    assert shopping_list["kjottdeig"] == 600


def test_create_raw_shopping_list_subtracts_pantry_amounts():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": {
                "ris": 1200,
                "kjottdeig": 600
            }
        }
    }

    shopping_list = create_raw_shopping_list(
        menu,
        number_of_people=4,
        pantry_items={"ris": 500}
    )

    assert shopping_list["ris"] == 700
    assert shopping_list["kjottdeig"] == 600


def test_create_rounded_shopping_list_rounds_up_packages():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": {
                "ris": 1200
            }
        }
    }

    shopping_list = create_rounded_shopping_list(menu, number_of_people=4)

    assert shopping_list["ris"]["packages_needed"] == 2


def test_create_rounded_shopping_list_skips_pantry_items():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": {
                "ris": 1200,
                "kjottdeig": 600
            }
        }
    }

    shopping_list = create_rounded_shopping_list(
        menu,
        number_of_people=4,
        pantry_items={"ris"}
    )

    assert "ris" not in shopping_list
    assert "kjottdeig" in shopping_list


def test_create_rounded_shopping_list_rounds_after_subtracting_pantry_amounts():
    menu = {
        "Mandag": {
            "name": "Testrett",
            "servings": 4,
            "ingredients": {
                "ris": 1200
            }
        }
    }

    shopping_list = create_rounded_shopping_list(
        menu,
        number_of_people=4,
        pantry_items={"ris": 500}
    )

    assert shopping_list["ris"]["needed_amount"] == 700
    assert shopping_list["ris"]["packages_needed"] == 1
