from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

client = MongoClient(os.getenv("MONGO_URI"))
db = client["flask_auth"]
users_collection = db["users"]

@app.route("/")
def home():
    return "MongoDB Connected Successfully!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            "email": email,
            "password": hashed_password
        })

        flash("Account created successfully. Please log in.", "info")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for("login"))

        session["user_email"] = email
        flash("Login successful. Welcome back!", "info")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", email=session["user_email"])

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))



# @app.route("/test-insert")
# def test_insert():
#     users_collection.insert_one({
#         "email": "test@example.com",
#         "password": "123456"
#     })
#     return "Test user inserted"


if __name__ == "__main__":
    app.run(debug=True)
