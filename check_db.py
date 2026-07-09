import sqlite3

conn = sqlite3.connect("recipe.db")
cursor = conn.cursor()

cursor.execute(
    "UPDATE admin SET password=? WHERE username=?",
    ("admin1234", "admin")
)

conn.commit()
conn.close()

print("Admin password updated successfully!")