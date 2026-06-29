import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path("data") / "matapp.db"
DEFAULT_USER_ID = 1


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: Path | None = None) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                number_of_people INTEGER,
                max_budget INTEGER,
                taco_friday INTEGER,
                wants_fish INTEGER,
                vegetarian_only INTEGER,
                exclude_vegetarian INTEGER,
                max_time_minutes INTEGER,
                menu_priority TEXT,
                excluded_allergens_json TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS pantry_items (
                user_id INTEGER,
                product_key TEXT,
                PRIMARY KEY (user_id, product_key)
            );

            CREATE TABLE IF NOT EXISTS saved_menus (
                user_id INTEGER PRIMARY KEY,
                menu_json TEXT,
                shopping_list_json TEXT,
                total_price REAL,
                created_at TEXT
            );
            """
        )
        connection.commit()
