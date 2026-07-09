import sqlite3

conn = sqlite3.connect("recipe.db")
cursor = conn.cursor()

print("Admin table:")
cursor.execute("SELECT * FROM admin")
print(cursor.fetchall())

conn.close()