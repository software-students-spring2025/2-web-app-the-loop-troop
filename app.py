import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv, dotenv_values
from flask_login import LoginManager, UserMixin, current_user, login_required
from auth import auth_bp

from helpers.add_entry import add_entry
from helpers.get_user import get_user

load_dotenv(override=True)

# global ref to db
db = None

def create_app():
    """
    Create and configure the Flask application.
    returns: app: the Flask application object
    """

    app = Flask(__name__)
    # load flask config from env variables
    config = dotenv_values()
    app.config.from_mapping(config)  

    # Creating secret key for a session HERE
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-in-.env")

    # made global db available
    global db
    cxn = MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)

    # setting up flask_login HERE
    loginManager = LoginManager()
    loginManager.init_app(app)
    # Where to redirect if @login_required fails
    loginManager.login_view = "auth.login"


    from auth import init_auth

    # define a simple User class that extends the imported UserMixin
    class User(UserMixin):
        def __init__(self, _id, username, pswdHash, nickname, profile_pic, user_entries, user_stats, join_date):
            self.id = str(_id)
            self.username = username
            self.pswddHash = pswdHash
            self.nickname = nickname if nickname is not None else username  # defaults to username if nickname not found
            self.profile_pic = profile_pic if profile_pic is not None else "static/nav-icons/profile-icon.svg"
            self.user_stats = user_stats if user_stats is not None else {"total_words": 0, "total_entries": 0}
            self.user_entries = user_entries if user_entries is not None else []
            self.join_date = join_date

    

    # USER LOADER
    @loginManager.user_loader
    def load_user(userId):
        userDoc = db.users.find_one({"_id":ObjectId(userId)})
        if not userDoc:
            return None
        return User(
            _id=userDoc["_id"],
            username = userDoc["username"],
            pswdHash=userDoc["pswdHash"],
            nickname=userDoc.get("nickname", userDoc["username"]),
            profile_pic=userDoc.get("profile_pic", "static/nav-icons/profile-icon.svg"), 
            user_stats=userDoc.get("user_stats", {"total_words": 0, "total_entries": 0}), 
            user_entries=userDoc.get("user_entries", []),
            join_date = userDoc["_id"].generation_time
        )
    init_auth(db, User)
    
    app.register_blueprint(auth_bp) # All routes in auth.py should be active now!

    @app.route("/") # root
    def home():
        """
        If user is logged in, show their home page (dashboard),
        else redirect to signup.
        """
        
        if current_user.is_authenticated:
            return redirect(url_for("auth.dashboard"))
        else:
            return redirect(url_for("auth.signup"))
        
        # email = "jane@abc.com"
        # user = get_user(email)
        # username = user["name"] if user and "name" in user else "User"
        # return render_template("journal_entry.html", username=username)
    
    @app.route("/submit_entry", methods=["POST"])
    def submit_entry():
        """
        
        """
        entry = request.form.get("entry")
        # return add_entry(entry)
        add_entry(entry) # CRITICAL
        email = "jane@abc.com"
        user = get_user(email)
        username = user["name"] if user and "name" in user else "User"
        return render_template("journal_entry.html", submitted=True, username=username)
          
    @app.route("/profile")
    def profile():
        now = datetime.now(timezone.utc) # convert utc to offset-aware type
        join_date = current_user.join_date.replace(tzinfo=timezone.utc)

        days_spent_writing = (now - join_date).days
        # days_spent_writing = 34 # uncomment to test
        days_spent_writing = max(1, days_spent_writing) # start counting from 1, instead of 0. so, 
                                                        # if you just join today, you still get stats

        if days_spent_writing > 0:
            avg_words_per_day = current_user.user_stats["total_words"] / days_spent_writing
        else:
            avg_words_per_day = 0

        return render_template("profile.html", current_user=current_user, 
                                days_spent_writing=days_spent_writing, 
                                avg_words_per_day=round(avg_words_per_day, 1))

    @app.route("/profile/stats")
    def stats():
        return render_template("stats.html", current_user=current_user)
    
    @app.errorhandler(Exception)
    def handle_error(e):
        """
        Output any errors - good for debugging.
        Args:
            e (Exception): The exception object.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        return render_template("error.html", error=e)

    return app

    # allow auth.pu to import the User class
    app.User = User
    return app

def get_db():
    """
    Helper function to retrieve the current MongoDB connection

    """
    global db
    return db


app = create_app()

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    FLASK_ENV = os.getenv("FLASK_ENV")
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")
    app.run(debug=True, port=FLASK_PORT)