from src.menu_generator import has_fish


def test_has_fish_returns_true_when_menu_contains_fish():
    menu = {
        "Mandag": {
            "name": "Laks med ris",
            "category": "fisk",
            "contains_fish": True
        },
        "Tirsdag": {
            "name": "Pasta",
            "category": "pasta",
            "contains_fish": False
        }
    }

    assert has_fish(menu) is True


def test_has_fish_returns_false_when_menu_has_no_fish():
    menu = {
        "Mandag": {
            "name": "Pasta",
            "category": "pasta",
            "contains_fish": False
        }
    }

    assert has_fish(menu) is False