import sqlite3
from contextlib import contextmanager

DB_NAME = "bizinsight.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_NAME)

    try:
        yield conn

    finally:
        conn.close()


def initialize_database():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT NOT NULL,
            sentiment REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()


def insert_feedback(review, sentiment):

    if not review.strip():
        raise ValueError("Review cannot be empty.")

    try:
        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO feedback (review, sentiment)
                VALUES (?, ?)
                """,
                (review, sentiment)
            )

            conn.commit()

    except sqlite3.Error as e:
        print(f"Insert Error: {e}")


def fetch_feedback():

    try:
        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
            SELECT review, sentiment, created_at
            FROM feedback
            ORDER BY created_at DESC
            """)

            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Fetch Error: {e}")
        return []


def clear_data():

    try:
        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("DELETE FROM feedback")

            conn.commit()

    except sqlite3.Error as e:
        print(f"Delete Error: {e}")


initialize_database()