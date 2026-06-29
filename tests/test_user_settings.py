import sqlite3

from src.database import init_db
from src.user_settings import load_user_settings, save_user_settings


def test_database_is_created(tmp_path):
    db_path = tmp_path / "matapp.db"

    init_db(db_path)

    assert db_path.exists()

    with sqlite3.connect(db_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {
        "user_settings",
        "pantry_items",
        "saved_menus"
    }.issubset(table_names)


def test_load_user_settings_returns_defaults_when_empty(tmp_path):
    settings = load_user_settings(tmp_path / "matapp.db")

    assert settings == {
        "number_of_people": 3,
        "max_budget": 900,
        "taco_friday": True,
        "wants_fish": True,
        "vegetarian_only": False,
        "exclude_vegetarian": False,
        "max_time_minutes": 40,
        "menu_priority": "Ingen spesiell prioritering",
        "excluded_allergens": []
    }


def test_user_settings_can_be_saved_and_loaded(tmp_path):
    db_path = tmp_path / "matapp.db"
    settings = {
        "number_of_people": 5,
        "max_budget": 1200,
        "taco_friday": False,
        "wants_fish": False,
        "vegetarian_only": True,
        "exclude_vegetarian": False,
        "max_time_minutes": 30,
        "menu_priority": "Raskest mulig",
        "excluded_allergens": ["gluten", "milk"]
    }

    save_user_settings(settings, db_path)

    assert load_user_settings(db_path) == settings


def test_user_settings_are_overwritten(tmp_path):
    db_path = tmp_path / "matapp.db"

    save_user_settings({"number_of_people": 2, "max_budget": 700}, db_path)
    save_user_settings({"number_of_people": 4, "max_budget": 1000}, db_path)

    loaded_settings = load_user_settings(db_path)

    assert loaded_settings["number_of_people"] == 4
    assert loaded_settings["max_budget"] == 1000
