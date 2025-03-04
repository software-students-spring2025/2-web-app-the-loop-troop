import os
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, jsonify, request, send_file, url_for
from flask_login import login_required, current_user
from bson.objectid import ObjectId
import plotly.graph_objects as go
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import gridfs
from io import BytesIO

from collections import defaultdict

load_dotenv(override=True)

cxn = MongoClient(os.getenv("MONGO_URI"))
db = cxn[os.getenv("MONGO_DBNAME")]
entries_collection = db["journalEntries"]
fs = gridfs.GridFS(db)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
@login_required
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

    print(days_spent_writing, avg_words_per_day)
    print(f"DEBUG: days_spent_writing = {days_spent_writing}, avg_words_per_day = {avg_words_per_day}")


    user_entries = list(entries_collection.find({"username": current_user.username}))

    current_user.user_entries =  user_entries

    print(days_spent_writing, avg_words_per_day)

    return render_template("profile.html", current_user=current_user, 
                            days_spent_writing=days_spent_writing, 
                            avg_words_per_day=round(avg_words_per_day, 1))


@profile_bp.route("/profile/stats")
@login_required
def stats():
    return render_template("stats.html", current_user=current_user)

@profile_bp.route("/profile/stats_data")
@login_required
def stats_data():
    try:
        user_entries = list(db.journalEntries.find({"username": current_user.username}))
        if not user_entries:
            return jsonify({"error": "No entries found."})

        # valculate longest and shortest entry word counts
        longest_entry = max(user_entries, key=lambda e: e.get("word_count", 0)).get("word_count", 0)
        shortest_entry = min(user_entries, key=lambda e: e.get("word_count", 0)).get("word_count", 0)

        # create helper to categorize the time of day
        def get_time_category(dt):
            hour = dt.hour
            if 6 <= hour < 12:
                return "Morning"
            elif 12 <= hour < 17:
                return "Afternoon"
            elif 17 <= hour < 21:
                return "Evening"
            else:
                return "Night"

        time_categories = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}
        for entry in user_entries:
            if "date_created" in entry:
                if isinstance(entry["date_created"], str):
                    dt = datetime.fromisoformat(entry["date_created"])
                else:
                    dt = entry["date_created"]
                category = get_time_category(dt)
                time_categories[category] += entry.get("word_count", 0)

        most_active_time = max(time_categories, key=time_categories.get)

        return jsonify({
            "longest_entry": longest_entry,
            "shortest_entry": shortest_entry,
            "active_time": most_active_time
        })

    except Exception as e:
        print(f"Stats Data Error: {e}")
        return jsonify({"error": "An error occurred while retrieving stats."})



@profile_bp.route("/profile/stats_graph")
@login_required
def stats_graph():
    """Returns JSON data for words written per week, month, or year with navigation support."""
    try:
        time_range = request.args.get("time_range", "week")
        offset = int(request.args.get("offset", 0))

        now = datetime.now(timezone.utc)
        user_entries = list(db.journalEntries.find({"username": current_user.username}))

        if not user_entries:
            return jsonify({"error": "Not enough data to generate a graph."})
        entries_dict = {}
        for entry in user_entries:
            if "date_created" not in entry:
                continue
            if isinstance(entry["date_created"], str):
                entry["date_created"] = datetime.fromisoformat(entry["date_created"])

            if time_range == "week":
                key = entry["date_created"].strftime("%Y-%m-%d")
            elif time_range == "month":
                key = entry["date_created"].strftime("%Y-%m")
            elif time_range == "year":
                key = entry["date_created"].strftime("%Y")
            else:
                return jsonify({"error": "Invalid time range."})
            entries_dict[key] = entries_dict.get(key, 0) + entry["word_count"]

        x_values, y_values = [], []
        if time_range == "week":
            start_of_week = (now - timedelta(days=now.weekday())) + timedelta(weeks=offset)
            for i in range(7):
                date_str = (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d")
                x_values.append(date_str)
                y_values.append(entries_dict.get(date_str, 0))
        elif time_range == "month":
            start_of_month = now.replace(day=1) + timedelta(weeks=offset * 4)
            for i in range(4):
                month_date = start_of_month - timedelta(weeks=4 * (3 - i))
                date_str = month_date.strftime("%Y-%m")
                x_values.append(date_str)
                y_values.append(entries_dict.get(date_str, 0))
        elif time_range == "year":
            start_of_year = now.replace(month=1, day=1) + timedelta(weeks=offset * 52)
            for i in range(4):
                year_date = start_of_year - timedelta(weeks=52 * (3 - i))
                date_str = year_date.strftime("%Y")
                x_values.append(date_str)
                y_values.append(entries_dict.get(date_str, 0))

        graph = go.Figure()
        graph.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            marker_color="black",
            text=y_values,
            textposition="inside",
            name="Words Written"
        ))

        graph.update_layout(
            title=f"Words by {time_range.capitalize()}",
            title_x=0.0,
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(tickmode="array", tickvals=x_values),
            yaxis=dict(showgrid=False, showticklabels=False),
            plot_bgcolor="#D3D3D3",
            font=dict(size=10, color="black"),
            margin=dict(t=50, b=40, l=20, r=20),
            height=400,
            bargap=0.2,
            showlegend=False,
            autosize=True,
        )

        return jsonify(graph.to_json())
    except Exception as e:
        print(f"Graph Error: {e}")
        return jsonify({"error": "An error occurred while generating the graph."})



@profile_bp.route("/profile/graph")
@login_required
def profile_graph():
    try:

        week_offset = int(request.args.get("week_offset", 0))

        # get the cur date and compute start of the reqd week
        now = datetime.now(timezone.utc)
        start_of_week = (now - timedelta(days=now.weekday())) + timedelta(weeks=week_offset)

        user_entries = list(db.journalEntries.find({"username": current_user.username}))

        if not user_entries:
            print("No entries found at all!")
            return jsonify({"error": "Not enough data to generate a graph."})

        # sum word counts per day
        entries_dict = {}

        for entry in user_entries:
            if "date_created" not in entry:
                print(f"Skipping entry, missing 'date_created': {entry}")
                continue  # skip invalid entries

            # convert to datetime if it's stored as a string
            if isinstance(entry["date_created"], str):
                entry["date_created"] = datetime.fromisoformat(entry["date_created"])

            date_str = entry["date_created"].strftime("%Y-%m-%d")
            entries_dict[date_str] = entries_dict.get(date_str, 0) + entry["word_count"]

        # make sure all days of the week are included
        x_dates = []
        y_words = []
        for i in range(7):  # go thru 7 days
            date = (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d")
            x_dates.append(date)
            y_words.append(entries_dict.get(date, 0))  # default is 0 if no entries

        graph = go.Figure()

        graph.add_trace(go.Bar(
            x=x_dates, 
            y=y_words, 
            marker_color="black",  
            text=y_words, 
            textposition="inside", 
            name="Words Written"
        ))

        graph.update_layout(
            title="Words by Week",
            title_x=0.0, 
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(
                tickformat="%b %d", 
                tickmode="array", 
                tickvals=x_dates
            ),  
            yaxis=dict(showgrid=False, showticklabels=False),
            plot_bgcolor="#D3D3D3",  
            font=dict(size=10, color="black"),
            margin=dict(t=50, b=40, l=20, r=20),
            height=400,
            bargap=0.2,  
            showlegend=False,
            autosize=True,
        )

        return jsonify(graph.to_json()) # return JSON data for frontend rendering

    except Exception as e:
        print(f"Graph Error: {e}")  # log any errors for debugging
        return jsonify({"error": "An error occurred while generating the graph."})
    

@profile_bp.route("/profile/update_nickname", methods=["POST"])
@login_required
def update_nickname():
    new_nickname = request.json.get("nickname")

    if not new_nickname or len(new_nickname.strip()) == 0:
        return jsonify({"error": "Nickname cannot be empty"}), 400

    # update the users nickname in mongo
    db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"nickname": new_nickname}}
    )

    return jsonify({"message": "Nickname updated!", "new_nickname": new_nickname})


@profile_bp.route("/profile/update_pfp", methods=["POST"])
@login_required
def update_pfp():
    """Handles profile picture uploads and stores them in MongoDB GridFS."""
    try:
        if "profile_pic" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["profile_pic"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif"}), 400

        # delete old profile pic from GridFS if exists
        user_doc = db.users.find_one({"_id": ObjectId(current_user.id)})
        if user_doc and "profile_pic" in user_doc and user_doc["profile_pic"]:
            try:
                fs.delete(ObjectId(user_doc["profile_pic"]))
            except:
                print("Old profile picture not found in GridFS, skipping delete.")

        # store the new image in GridFS
        file_id = fs.put(file, filename=secure_filename(f"{current_user.id}.jpg"), content_type=file.content_type)

        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"profile_pic": str(file_id)}}
        )

        return jsonify({"new_pfp_url": url_for("profile.get_profile_pic", user_id=current_user.id)})

    except Exception as e:
        print(f"Error uploading profile picture: {e}")
        return jsonify({"error": "An error occurred while uploading the profile picture."}), 500


@profile_bp.route("/profile-pic/<user_id>")
def get_profile_pic(user_id):
    """Serves the profile picture from MongoDB GridFS."""
    user_doc = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user_doc or "profile_pic" not in user_doc or not user_doc["profile_pic"]:
        return send_file("static/nav-icons/profile-icon.svg", mimetype="image/svg+xml")  # return default profile pic

    try:
        file_id = ObjectId(user_doc["profile_pic"])
        file_data = fs.get(file_id)
        return send_file(BytesIO(file_data.read()), mimetype=file_data.content_type)
    
    except Exception as e:
        print(f"Error fetching profile pic: {e}")
        return send_file("static/nav-icons/profile-icon.svg", mimetype="image/svg+xml")  # default image fallback