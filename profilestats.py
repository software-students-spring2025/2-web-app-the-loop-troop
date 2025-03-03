import os
from datetime import datetime, timezone
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
import plotly.graph_objects as go

profile_bp = Blueprint("profile", __name__)

################ hardcoded fake data to test stats. this code should be removed
################ after the journal entries db is set up
fake_entries = [
    {
        "_id": ObjectId(),
        "user_id": ObjectId("65f23c8e2d4a4b3a1a123456"),
        "content": "Today was a peaceful day. I reflected on my journey.",
        "word_count": 10,
        "date_created": datetime(2025, 2, 28, 14, 30, tzinfo=timezone.utc),
    },
    {
        "_id": ObjectId(),
        "user_id": ObjectId("65f23c8e2d4a4b3a1a123456"),
        "content": "Wrote some poetry. Feeling inspired.",
        "word_count": 7,
        "date_created": datetime(2025, 3, 1, 9, 15, tzinfo=timezone.utc),
    },
    {
        "_id": ObjectId(),
        "user_id": ObjectId("65f23c8e2d4a4b3a1a123456"),
        "content": "Late night journaling. So many thoughts swirling.",
        "word_count": 9,
        "date_created": datetime(2025, 3, 2, 23, 45, tzinfo=timezone.utc),
    }
]

################ 

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

    current_user.user_entries = fake_entries

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
    
    # get the current date
    now = datetime.now(timezone.utc)

    # user_entries = current_user.user_entries
    user_entries = fake_entries

    if not user_entries:
        print("No entries found at all!")
        return jsonify({"error": "Not enough data to generate a graph."})

    # Filter journal entries to only include entries from the last 7 days
    # recent_entries = [
    #     entry for entry in current_user.user_entries
    #     if (now - entry["date_created"]).days <= 7
    # ]

    # if not recent_entries:
    #     print("⚠️ No entries in the last 7 days!")
    #     return jsonify({"error": "Not enough data to generate a graph."})
    

    # convert fake_entries to x (dates) and y (word counts)
    x_dates = [entry["date_created"].strftime("%Y-%m-%d") for entry in fake_entries]
    y_words = [entry["word_count"] for entry in fake_entries]


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
        xaxis=dict(tickformat="%b %d", tickmode="array", tickvals=x_dates),  
        yaxis=dict(showgrid=False, showticklabels=False),
        plot_bgcolor="#D3D3D3",  
        font=dict(size=10, color="black"),
        margin=dict(t=50, b=40, l=20, r=20),
        height=400,
        bargap=0.2,  
        showlegend=False,
        width=None,
        autosize=True,
        )

    return jsonify(graph.to_json())  # return JSON data for frontend rendering
