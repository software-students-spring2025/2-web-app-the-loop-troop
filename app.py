import os
import datetime
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv, dotenv_values

from helpers.add_entry import add_entry
from helpers.get_user import get_user

load_dotenv(override=True)


def create_app():
    """
    Create and configure the Flask application.
    returns: app: the Flask application object
    """

    app = Flask(__name__)
    # load flask config from env variables
    config = dotenv_values()
    app.config.from_mapping(config)

    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)

    @app.route("/") # root
    def home():
        """
        Route for the home page.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        email = "jane@abc.com"
        user = get_user(email)
        username = user["name"] if user and "name" in user else "User"
        return render_template("journal_entry.html", username=username)
    
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


app = create_app()

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    FLASK_ENV = os.getenv("FLASK_ENV")
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")
    app.run(debug=True, port=FLASK_PORT)