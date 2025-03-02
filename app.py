import os
import datetime
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv, dotenv_values
from flask_login import LoginManager, UserMixin
from auth import auth_bp

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
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
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

    # define a simple User class that extends the imported UserMixin
    class User(UserMixin):
        def __init__(self, _id, username, pswdHash):
            self.id = str(_id)
            self.username = username
            self.pswddHash = pswdHash

    # USER LOADER
    @loginManager.user_loader
    def load_user(userId):
        userDoc = db.users.find_one({"_id":ObjectId(userId)})
        if not userDoc:
            return None
        return User(
            _id=userDoc["_id"],
            username = userDoc["username"],
            pswdHash=userDoc["pswdHash"]
        )
    
    app.register_blueprint(auth_bp) # All routes in auth.py should be active now!

    @app.route("/")
    def home():
        """
        Route for the home page.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        users = db.users.find()  # Fetch users from MongoDB
        return render_template("index.html", users=users)

    
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

    app.run(port=FLASK_PORT)