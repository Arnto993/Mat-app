import json
from datetime import datetime, timezone
from pathlib import Path

from src.database import DEFAULT_USER_ID, get_connection, init_db


DEFAULT_USER_SETTINGS = {
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


def _default_settings_copy() -> dict:
    settings = DEFAULT_USER_SETTINGS.copy()
    settings["excluded_allergens"] = DEFAULT_USER_SETTINGS["excluded_allergens"].copy()
    return settings


def _bool_to_int(value: bool) -> int:
    return 1 if value else 0


def _load_json_list(value: str | None) -> list[str]:
    if not value:
        return []

    try:
        loaded_value = json.loads(value)
    except json.JSONDecodeError:
        return []

    if not isinstance(loaded_value, list):
        return []

    return [
        item
        for item in loaded_value
        if isinstance(item, str)
    ]


def load_user_settings(db_path: Path | None = None) -> dict:
    init_db(db_path)

    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (DEFAULT_USER_ID,)
        ).fetchone()

    if row is None:
        return _default_settings_copy()

    defaults = _default_settings_copy()
    row_keys = set(row.keys())

    return {
        "number_of_people": row["number_of_people"] or defaults["number_of_people"],
        "max_budget": row["max_budget"] or defaults["max_budget"],
        "taco_friday": bool(row["taco_friday"]),
        "wants_fish": bool(row["wants_fish"]),
        "vegetarian_only": bool(row["vegetarian_only"]),
        "exclude_vegetarian": (
            bool(row["exclude_vegetarian"])
            if "exclude_vegetarian" in row_keys
            else defaults["exclude_vegetarian"]
        ),
        "max_time_minutes": (
            row["max_time_minutes"] or defaults["max_time_minutes"]
        ),
        "menu_priority": row["menu_priority"] or defaults["menu_priority"],
        "excluded_allergens": _load_json_list(row["excluded_allergens_json"])
    }


def save_user_settings(settings: dict, db_path: Path | None = None) -> None:
    init_db(db_path)

    values = _default_settings_copy()
    values.update(settings)

    excluded_allergens_json = json.dumps(
        values.get("excluded_allergens", []),
        ensure_ascii=False
    )
    updated_at = datetime.now(timezone.utc).isoformat()

    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO user_settings (
                user_id,
                number_of_people,
                max_budget,
                taco_friday,
                wants_fish,
                vegetarian_only,
                exclude_vegetarian,
                max_time_minutes,
                menu_priority,
                excluded_allergens_json,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                number_of_people = excluded.number_of_people,
                max_budget = excluded.max_budget,
                taco_friday = excluded.taco_friday,
                wants_fish = excluded.wants_fish,
                vegetarian_only = excluded.vegetarian_only,
                exclude_vegetarian = excluded.exclude_vegetarian,
                max_time_minutes = excluded.max_time_minutes,
                menu_priority = excluded.menu_priority,
                excluded_allergens_json = excluded.excluded_allergens_json,
                updated_at = excluded.updated_at
            """,
            (
                DEFAULT_USER_ID,
                int(values["number_of_people"]),
                int(values["max_budget"]),
                _bool_to_int(values["taco_friday"]),
                _bool_to_int(values["wants_fish"]),
                _bool_to_int(values["vegetarian_only"]),
                _bool_to_int(values["exclude_vegetarian"]),
                int(values["max_time_minutes"]),
                values["menu_priority"],
                excluded_allergens_json,
                updated_at
            )
        )
        connection.commit()
