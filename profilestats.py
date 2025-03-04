import os
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from bson.objectid import ObjectId
import plotly.graph_objects as go
from pymongo import MongoClient
from dotenv import load_dotenv

from collections import defaultdict

load_dotenv(override=True)

cxn = MongoClient(os.getenv("MONGO_URI"))
db = cxn[os.getenv("MONGO_DBNAME")]
entries_collection = db["journalEntries"]

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