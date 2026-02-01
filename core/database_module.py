import sqlite3

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bio TEXT NOT NULL,
            openness REAL,
            conscientiousness REAL,
            extraversion REAL,
            agreeableness REAL,
            neuroticism REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    except Exception as e:
        print(f"Database error: {e}")
        return False