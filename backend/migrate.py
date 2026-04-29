import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "data", "history.db")

def migrate():
    if not os.path.exists(db_path):
        print("No database found, tables will be created on startup")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns_to_add = [
        ("workflows", "visibility", "TEXT DEFAULT 'private'"),
        ("workflows", "team_id", "TEXT"),
        ("workflows", "creator_name", "TEXT"),
        ("workflows", "creator_email", "TEXT"),
    ]

    for table, column, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            print(f"Added {table}.{column}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()
    print("Migration complete")

if __name__ == "__main__":
    migrate()
