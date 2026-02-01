import sqlite3

conn = sqlite3.connect('profiles.db')
cursor = conn.cursor()

# Delete all old profiles
cursor.execute("DELETE FROM profiles")
conn.commit()
conn.close()
print("Old profiles deleted. Database is clean!")
