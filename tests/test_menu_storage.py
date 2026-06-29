from src.menu_storage import load_last_menu, save_last_menu


def test_load_last_menu_returns_none_when_empty(tmp_path):
    assert load_last_menu(tmp_path / "matapp.db") is None


def test_last_menu_can_be_saved_and_loaded(tmp_path):
    db_path = tmp_path / "matapp.db"
    menu = {
        "Mandag": {
            "name": "Risrett",
            "ingredients": [
                {"product_id": "rice_jasmin_1000", "amount": 400, "unit": "g"}
            ]
        }
    }
    shopping_list = {
        "rice_jasmin_1000": {
            "product_id": "rice_jasmin_1000",
            "display_name": "Jasminris",
            "estimated_total_price": 35
        }
    }

    save_last_menu(menu, shopping_list, 35.0, db_path)

    assert load_last_menu(db_path) == {
        "menu": menu,
        "shopping_list": shopping_list,
        "total_price": 35.0
    }


def test_last_menu_is_overwritten(tmp_path):
    db_path = tmp_path / "matapp.db"

    save_last_menu({"Mandag": {"name": "Risrett"}}, {}, 35.0, db_path)
    save_last_menu({"Tirsdag": {"name": "Pasta"}}, {}, 42.0, db_path)

    assert load_last_menu(db_path) == {
        "menu": {"Tirsdag": {"name": "Pasta"}},
        "shopping_list": {},
        "total_price": 42.0
    }
