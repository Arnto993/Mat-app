from src.pantry_storage import load_pantry_items, save_pantry_items


def test_pantry_items_can_be_saved_and_loaded(tmp_path):
    db_path = tmp_path / "matapp.db"

    save_pantry_items(["rice_jasmin_1000", "egg_12"], db_path)

    assert load_pantry_items(db_path) == ["egg_12", "rice_jasmin_1000"]


def test_pantry_items_are_overwritten(tmp_path):
    db_path = tmp_path / "matapp.db"

    save_pantry_items(["rice_jasmin_1000", "egg_12"], db_path)
    save_pantry_items(["chopped_tomatoes_400"], db_path)

    assert load_pantry_items(db_path) == ["chopped_tomatoes_400"]


def test_pantry_items_skip_empty_and_duplicate_keys(tmp_path):
    db_path = tmp_path / "matapp.db"

    save_pantry_items(["egg_12", "", "egg_12"], db_path)

    assert load_pantry_items(db_path) == ["egg_12"]
