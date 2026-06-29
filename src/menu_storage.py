import json
from datetime import datetime, timezone
from pathlib import Path

from src.database import DEFAULT_USER_ID, get_connection, init_db


def save_last_menu(
    menu: dict,
    shopping_list: dict,
    total_price: float,
    db_path: Path | None = None
) -> None:
    init_db(db_path)

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO saved_menus (
                user_id,
                menu_json,
                shopping_list_json,
                total_price,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                menu_json = excluded.menu_json,
                shopping_list_json = excluded.shopping_list_json,
                total_price = excluded.total_price,
                created_at = excluded.created_at
            """,
            (
                DEFAULT_USER_ID,
                json.dumps(menu, ensure_ascii=False),
                json.dumps(shopping_list, ensure_ascii=False),
                float(total_price),
                created_at
            )
        )
        connection.commit()


def load_last_menu(db_path: Path | None = None) -> dict | None:
    init_db(db_path)

    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT menu_json, shopping_list_json, total_price
            FROM saved_menus
            WHERE user_id = ?
            """,
            (DEFAULT_USER_ID,)
        ).fetchone()

    if row is None:
        return None

    try:
        menu = json.loads(row["menu_json"])
        shopping_list = json.loads(row["shopping_list_json"])
    except json.JSONDecodeError:
        return None

    return {
        "menu": menu,
        "shopping_list": shopping_list,
        "total_price": row["total_price"]
    }
