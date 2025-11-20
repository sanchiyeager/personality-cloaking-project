#Harsh's work

import sqlite3

DB_NAME = "database.db"

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
                profile_data.get("bio"),
                profile_data.get("openness"),
                profile_data.get("conscientiousness"),
                profile_data.get("extraversion"),
                profile_data.get("agreeableness"),
                profile_data.get("neuroticism"),
            )
        )

        conn.commit()
        profile_id = cursor.lastrowid
        conn.close()

        return True, profile_id

    except sqlite3.Error:
        return False, None
