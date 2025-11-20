import sqlite3

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    with open("schema.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()

init_db()

def save_profile(profile_data):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO profiles (
                bio,
                openness,
                conscientiousness,
                extraversion,
                agreeableness,
                neuroticism
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                profile_data["bio"],
                profile_data["personality"]["openness"],
                profile_data["personality"]["conscientiousness"],
                profile_data["personality"]["extraversion"],
                profile_data["personality"]["agreeableness"],
                profile_data["personality"]["neuroticism"],
            )
        )

        conn.commit()
        conn.close()
        return True

    except Exception:
        return False

