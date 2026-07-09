from flask import Flask, render_template, request, jsonify, redirect, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import requests
import sqlite3

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = Flask(__name__)
import database
app.secret_key = "recipebasket123"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

API_KEY = os.getenv("SPOONACULAR_API_KEY")

def get_db_connection():
    conn = sqlite3.connect(
        "recipe.db",
        timeout=30,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    return render_template("index.html", username=username)

@app.route("/recipe")
def recipe():

    if "user" not in session:
        return redirect("/login")

    return render_template("recipe.html")

@app.route("/search")
def search():

    if "user" not in session:
        return jsonify({"error": "Please login first"}), 401

    query = request.args.get("query")

    url = "https://api.spoonacular.com/recipes/complexSearch"

    params = {
        "query": query,
        "number": 5,
        "addRecipeInformation": True,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)

    return jsonify(response.json())

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        existing_user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            return "Email already registered."

        hashed_password = generate_password_hash(password)

        conn.execute(
            "INSERT INTO users(username, email, password) VALUES(?,?,?)",
            (username, email, hashed_password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user"] = username

            return redirect("/")

        else:

            return "Invalid username or password"

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        conn.close()

        if user:
            return render_template("reset_password.html", email=email)

        return "Email not found."

    return render_template("forgot_password.html")


@app.route("/reset_password", methods=["POST"])
def reset_password():

    email = request.form["email"]
    new_password = request.form["new_password"]

    conn = get_db_connection()

    hashed_password = generate_password_hash(new_password)

    conn.execute(
        "UPDATE users SET password=? WHERE email=?",
        (hashed_password, email)
    )

    conn.commit()
    conn.close()

    return redirect("/login")

@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE username=?",
        (session["user"],)
    ).fetchone()
    conn.close()

    return render_template("profile.html", user=user)
@app.route("/add_favorite", methods=["POST"])
def add_favorite():

    print("=== ADD FAVORITE ROUTE CALLED ===")

    if "user" not in session:
        print("User not logged in")
        return jsonify({"success": False})

    recipe_id = request.form["recipe_id"]
    recipe_name = request.form["recipe_name"]
    recipe_image = request.form["recipe_image"]

    print("Username:", session["user"])
    print("Recipe ID:", recipe_id)
    print("Recipe Name:", recipe_name)

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO favorites(username, recipe_id, recipe_name, recipe_image)
        VALUES(?,?,?,?)
        """,
        (session["user"], recipe_id, recipe_name, recipe_image)
    )

    conn.commit()
    conn.close()

    print("Favorite saved successfully!")

    return jsonify({"success": True})
@app.route("/get_favorites")
def get_favorites():

    if "user" not in session:
        return jsonify([])

    conn = get_db_connection()

    favorites = conn.execute(
        "SELECT recipe_name, recipe_image FROM favorites WHERE username=?",
        (session["user"],)
    ).fetchall()
    conn.close()

    return jsonify([row["recipe_name"] for row in favorites])
@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():

    if "user" not in session:
        return jsonify({"success": False})

    recipe_name = request.form["recipe_name"]

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM favorites WHERE username=? AND recipe_name=?",
        (session["user"], recipe_name)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})
@app.route("/add_shopping", methods=["POST"])
def add_shopping():

    if "user" not in session:
        return jsonify({"success": False})

    item = request.form["item"]

    conn = get_db_connection()

    user_id = conn.execute(
        "SELECT id FROM users WHERE username=?",
        (session["user"],)
    ).fetchone()["id"]

    existing = conn.execute(
        "SELECT * FROM shopping_list WHERE user_id=? AND item=?",
        (user_id, item)
    ).fetchone()

    if not existing:
        conn.execute(
            "INSERT INTO shopping_list(user_id, item) VALUES(?, ?)",
            (user_id, item)
        )

    conn.commit()
    conn.close()

    return jsonify({"success": True})
@app.route("/get_shopping")
def get_shopping():

    if "user" not in session:
        return jsonify([])

    conn = get_db_connection()

    items = conn.execute("""
        SELECT item
        FROM shopping_list
        WHERE user_id = (
            SELECT id FROM users WHERE username=?
        )
    """, (session["user"],)).fetchall()

    conn.close()

    return jsonify([row["item"] for row in items])
@app.route("/remove_shopping", methods=["POST"])
def remove_shopping():

    if "user" not in session:
        return jsonify({"success": False})

    item = request.form["item"]

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM shopping_list
        WHERE user_id = (
            SELECT id FROM users WHERE username=?
        )
        AND item=?
    """, (session["user"], item))

    conn.commit()
    conn.close()

    return jsonify({"success": True})
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()

    favorites = conn.execute(
        """
        SELECT recipe_name, recipe_image
        FROM favorites
        WHERE username=?
        """,
        (session["user"],)
    ).fetchall()

    shopping = conn.execute("""
        SELECT item
        FROM shopping_list
        WHERE user_id = (
            SELECT id FROM users WHERE username=?
        )
    """, (session["user"],)).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["user"],
        favorites=favorites,
        shopping=shopping
    )
@app.route("/add_review", methods=["POST"])
def add_review():

    if "user" not in session:
        return jsonify({"success": False})

    recipe_id = request.form["recipe_id"]
    recipe_name = request.form["recipe_name"]
    rating = request.form["rating"]
    comment = request.form["comment"]

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO reviews(username, recipe_id, recipe_name, rating, comment)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session["user"], recipe_id, recipe_name, rating, comment)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})
@app.route("/get_reviews")
def get_reviews():

    recipe_id = request.args.get("recipe_id")

    conn = get_db_connection()

    reviews = conn.execute(
        """
        SELECT username, rating, comment
        FROM reviews
        WHERE recipe_id=?
        ORDER BY id DESC
        """,
        (recipe_id,)
    ).fetchall()

    conn.close()

    return jsonify([
        {
            "username": row["username"],
            "rating": row["rating"],
            "comment": row["comment"]
        }
        for row in reviews
    ])
@app.route("/get_average_rating")
def get_average_rating():

    recipe_id = request.args.get("recipe_id")

    conn = get_db_connection()

    result = conn.execute("""
        SELECT
            AVG(rating) AS average_rating,
            COUNT(*) AS total_reviews
        FROM reviews
        WHERE recipe_id=?
    """, (recipe_id,)).fetchone()

    conn.close()

    return jsonify({
        "average": round(result["average_rating"], 1) if result["average_rating"] else 0,
        "count": result["total_reviews"]
    })


@app.route("/update_profile", methods=["POST"])
def update_profile():

    if "user" not in session:
        return redirect("/login")

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    profile_image = request.files["profile_image"]

    conn = get_db_connection()

    try:

        if password.strip() == "":
            conn.execute(
                "UPDATE users SET username=?, email=? WHERE username=?",
                (username, email, session["user"])
            )
        else:
            hashed_password = generate_password_hash(password)

            conn.execute(
                "UPDATE users SET username=?, email=?, password=? WHERE username=?",
                (username, email, hashed_password, session["user"])
            )

        if profile_image and profile_image.filename != "":
            filename = secure_filename(profile_image.filename)

            profile_image.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

            conn.execute(
                "UPDATE users SET profile_image=? WHERE username=?",
                (filename, username)
            )

        conn.commit()

    finally:
        conn.close()

    session["user"] = username

    return redirect("/profile")
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db_connection()

        admin = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()


        conn.close()

        if admin:
            session["admin"] = username
            return redirect("/admin_dashboard")

        return "Invalid Admin Login"

    return render_template("admin_login.html")
@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    total_users = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_favorites = conn.execute(
        "SELECT COUNT(*) FROM favorites"
    ).fetchone()[0]

    total_reviews = conn.execute(
        "SELECT COUNT(*) FROM reviews"
    ).fetchone()[0]

    total_shopping = conn.execute(
        "SELECT COUNT(*) FROM shopping_list"
    ).fetchone()[0]
    total_orders = conn.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    recent_users = conn.execute("""
        SELECT username, email
        FROM users
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_favorites=total_favorites,
        total_reviews=total_reviews,
        total_shopping=total_shopping,
        total_orders=total_orders,
        recent_users=recent_users
    )
@app.route("/admin_users")
def admin_users():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    users = conn.execute(
        "SELECT id, username, email FROM users"
    ).fetchall()

    conn.close()

    return render_template(
        "users.html",
        users=users
    )
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()

    conn.close()

    return redirect("/admin_users")
@app.route("/admin_logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin_login")
@app.route("/admin_reviews")
def admin_reviews():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    reviews = conn.execute("""
        SELECT id, username, recipe_name, rating, comment
        FROM reviews
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_reviews.html",
        reviews=reviews
    )
@app.route("/delete_review/<int:review_id>")
def delete_review(review_id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM reviews WHERE id=?",
        (review_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin_reviews")
@app.route("/admin_favorites")
def admin_favorites():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    favorites = conn.execute("""
        SELECT id,
               username,
               recipe_name,
               recipe_image
        FROM favorites
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_favorites.html",
        favorites=favorites
    )
@app.route("/delete_favorite/<int:favorite_id>")
def delete_favorite(favorite_id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM favorites WHERE id=?",
        (favorite_id,)
    )

    conn.commit()

    conn.close()

    return redirect("/admin_favorites")
@app.route("/admin_shopping")
def admin_shopping():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    shopping = conn.execute("""
        SELECT shopping_list.id,
               users.username,
               shopping_list.item
        FROM shopping_list
        JOIN users
        ON shopping_list.user_id = users.id
        ORDER BY shopping_list.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_shopping.html",
        shopping=shopping
    )
@app.route("/delete_shopping/<int:item_id>")
def delete_shopping(item_id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM shopping_list WHERE id=?",
        (item_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin_shopping")
@app.route("/request_order", methods=["POST"])
def request_order():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    recipe_name = request.form["recipe_name"]
    ingredients = request.form["ingredients"]
    conn = get_db_connection()

    # Get user's email from database
    user = conn.execute(
        "SELECT email FROM users WHERE username=?",
        (username,)
    ).fetchone()

    email = user["email"]

    conn.execute("""
        INSERT INTO orders
        (username, email, recipe_name, ingredients)
        VALUES (?, ?, ?, ?)
    """, (username, email, recipe_name, ingredients))

    conn.commit()
    conn.close()

    return "✅ Your request has been sent to the Recipe Basket admin."
@app.route("/admin_orders")
def admin_orders():

    conn = get_db_connection()

    orders = conn.execute(
        "SELECT * FROM orders ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "admin_orders.html",
        orders=orders
    )
@app.route("/approve_order/<int:order_id>")
def approve_order(order_id):

    conn = get_db_connection()

    conn.execute(
        "UPDATE orders SET status='Approved' WHERE id=?",
        (order_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin_orders")
@app.route("/reject_order/<int:order_id>")
def reject_order(order_id):

    conn = get_db_connection()

    conn.execute(
        "UPDATE orders SET status='Rejected' WHERE id=?",
        (order_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin_orders")
if __name__ == "__main__":
    app.run(debug=True)