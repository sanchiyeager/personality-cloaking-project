CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bio TEXT NOT NULL,
    openness REAL,
    conscientiousness REAL,
    extraversion REAL,
    agreeableness REAL,
    neuroticism REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);