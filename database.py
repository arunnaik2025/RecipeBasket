import sqlite3

connection = sqlite3.connect("recipe.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    profile_image TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS shopping_list(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    recipe_id INTEGER NOT NULL,
    recipe_name TEXT NOT NULL,
    recipe_image TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    recipe_id INTEGER NOT NULL,
    recipe_name TEXT NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT NOT NULL
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO admin(username,password)
VALUES('admin','admin123')
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    email TEXT,

    recipe_name TEXT,

    ingredients TEXT,

    status TEXT DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")
connection.commit()

connection.close()

print("Database created successfully!")