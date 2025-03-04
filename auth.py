import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# creating the blueprint
auth_bp = Blueprint("auth", __name__, template_folder="templates")

_db = None
User = None

def init_auth(db, user_class):
    """Initialize references so we can avoid circular imports"""
    global _db, User
    _db = db
    User = user_class

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # checking for existing user using pymongo
        existingUser = _db.users.find_one({"username": username})
        if existingUser:
            # flash - stores one-time msg int he user's session to display it on the next page load
            flash("Oops! That username is already taken!")
            return redirect(url_for("auth.signup"))
        # Note: passwords need to be hashed! 
        # WARNING: Fails on certain computers!
        pswdHash = generate_password_hash(password)
        pswdHash = password
        result = _db.users.insert_one({
            "username": username, 
            "pswdHash": pswdHash,
            "nickname": username, #username by default
            "profile_pic": "static/nav-icons/profile-icon.svg",
            "user_stats":{
                "total_words": 0,
                "total_entries": 0
            },
            "user_entries": []
            })
        newId = result.inserted_id

        # User object is created here!
        user = User(
            _id=newId, 
            username=username, 
            pswdHash = pswdHash,
            nickname=username,  # defaults to username
            profile_pic="static/nav-icons/profile-icon.svg",
            user_entries=[],
            user_stats={"total_words": 0, "total_entries": 0}
        )
        login_user(user)
        flash("Alrighty, you are good to go!")
        return redirect(url_for("auth.dashboard"))
    
    # flask function to look into the templates folder
    return render_template("signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        userDoc = _db.users.find_one({"username": username})
        if userDoc and check_password_hash(userDoc["pswdHash"], password):
            user = User(
                _id=userDoc["_id"], 
                username=userDoc["username"], 
                pswdHash=userDoc["pswdHash"],
                nickname=userDoc.get("nickname"),
                profile_pic=userDoc.get("profile_pic"),
                user_entries=userDoc.get("user_entries"),
                user_stats=userDoc.get("user_stats")
            )
            login_user(user)
            # store the app's current start marker session
            session['app_start'] = current_app.config['APP_START']
            flash("Thank you for using our Journal App!")
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
    return render_template("journal_entry2.html", current_user=current_user)