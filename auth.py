import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# creating the blueprint
auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    from app import get_db, User
    db = get_db()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # checking for existing user using pymongo
        existingUser = db.users.find_one({"username": username})
        if existingUser:
            # flash - stores one-time msg int he user's session to display it on the next page load
            flash("Oops! That username is already taken!")
            return redirect(url_for("auth.signup"))
        # Note: passwords need to be hashed! 
        pswdHash = generate_password_hash(password)
        result = db.users.insert_one({"username": username, "password_hash": password_hash})
        newId = result.insertedId

        # User object is created here!
        user = User(
            _id=newId, username=username, pswdHash = pswdHash
        )
        login_user(user)
        flash("Alrighty, you are good to go!")
        return redirect(url_for("auth.dashboard"))
    
    # flask function to look into the templates folder
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from app import get_db, User
    db = get_db()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        userDoc = db.users.find_one({"username": username})
        if userDoc and check_password_hash(userDoc["password_hash"], password):
            user = User(
                _id=userDoc["_id"], username=userDoc["username"], pswdHash=userDoc["pswdHash"]
            )
            login_user(user)
            flash("Nice, you are loggen in!")
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Oops..invalid credentials, my friend, try again.")
            return redirect(url_for("auth.login"))
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Bye for now! Don't forget to stop by tomorrow!")
    return redirect(url_for("auth.login")) # redirecting ot login page

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", current_user=current_user)
