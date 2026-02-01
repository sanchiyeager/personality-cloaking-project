# view_db.py
import sqlite3

conn = sqlite3.connect('profiles.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM profiles")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
