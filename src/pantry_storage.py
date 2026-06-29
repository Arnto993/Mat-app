from pathlib import Path

from src.database import DEFAULT_USER_ID, get_connection, init_db


def load_pantry_items(db_path: Path | None = None) -> list[str]:
    init_db(db_path)

    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT product_key
            FROM pantry_items
            WHERE user_id = ?
            ORDER BY product_key
            """,
            (DEFAULT_USER_ID,)
        ).fetchall()

    return [row["product_key"] for row in rows]


def save_pantry_items(product_keys: list[str], db_path: Path | None = None) -> None:
    init_db(db_path)

    seen_keys = set()
    normalized_keys = []

    for product_key in product_keys:
        if not product_key or product_key in seen_keys:
            continue

        seen_keys.add(product_key)
        normalized_keys.append(product_key)

    with get_connection(db_path) as connection:
        connection.execute(
            "DELETE FROM pantry_items WHERE user_id = ?",
            (DEFAULT_USER_ID,)
        )
        connection.executemany(
            """
            INSERT INTO pantry_items (user_id, product_key)
            VALUES (?, ?)
            """,
            [
                (DEFAULT_USER_ID, product_key)
                for product_key in normalized_keys
            ]
        )
        connection.commit()
