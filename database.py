import sqlite3

conn = sqlite3.connect("bizinsight.db", check_same_thread=False)
cursor = conn.cursor()

# We create a feedback table to store the original review, cleaned review, sentiment score, and timestamp. The original_review column is marked as UNIQUE to prevent duplicate entries.
cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_review TEXT UNIQUE,
    cleaned_review TEXT,
    sentiment REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# We check if the old 'review' column exists and migrate data to the new schema if necessary. This ensures that existing reviews are not lost when we update our database structure to include both original and cleaned reviews.
cursor.execute("PRAGMA table_info(feedback)")
columns = [col[1] for col in cursor.fetchall()]
if 'review' in columns and 'original_review' not in columns:
    print("Migrating old data to new schema...")
    # Add new columns if they don't exist
    if 'original_review' not in columns:
        cursor.execute("ALTER TABLE feedback ADD COLUMN original_review TEXT")
    if 'cleaned_review' not in columns:
        cursor.execute("ALTER TABLE feedback ADD COLUMN cleaned_review TEXT")
    # Copy data from old 'review' column
    cursor.execute("UPDATE feedback SET original_review = review, cleaned_review = review WHERE original_review IS NULL")
    # Optionally drop old column (SQLite doesn't support DROP COLUMN, so we recreate table)
    cursor.execute("""
        CREATE TABLE feedback_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_review TEXT UNIQUE,
            cleaned_review TEXT,
            sentiment REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        INSERT INTO feedback_new (id, original_review, cleaned_review, sentiment, created_at)
        SELECT id, original_review, cleaned_review, sentiment, created_at FROM feedback
    """)
    cursor.execute("DROP TABLE feedback")
    cursor.execute("ALTER TABLE feedback_new RENAME TO feedback")
    conn.commit()
    print("Migration complete.")

# The insert_feedback function allows us to add new feedback entries to the database. It takes the original review, cleaned review, and sentiment score as input and inserts them into the feedback table. 
def insert_feedback(original_review, cleaned_review, sentiment):
    cursor.execute(
        "INSERT OR IGNORE INTO feedback (original_review, cleaned_review, sentiment) VALUES (?, ?, ?)",
        (original_review, cleaned_review, sentiment)
    )
    conn.commit()

# The fetch_feedback function retrieves all feedback entries from the database, returning the original review, cleaned review, sentiment score, and creation timestamp for each entry. 
def fetch_feedback():
    cursor.execute("SELECT original_review, cleaned_review, sentiment, created_at FROM feedback")
    return cursor.fetchall()

# The clear_data function deletes all entries from the feedback table, which can be useful for resetting the database during development or testing.
def clear_data():
    cursor.execute("DELETE FROM feedback")
    conn.commit()