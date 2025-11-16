CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bio TEXT NOT NULL,
    openness REAL CHECK (openness BETWEEN 0 AND 1),
    conscientiousness REAL CHECK (conscientiousness BETWEEN 0 AND 1),
    extraversion REAL CHECK (extraversion BETWEEN 0 AND 1),
    agreeableness REAL CHECK (agreeableness BETWEEN 0 AND 1),
    neuroticism REAL CHECK (neuroticism BETWEEN 0 AND 1)
);
