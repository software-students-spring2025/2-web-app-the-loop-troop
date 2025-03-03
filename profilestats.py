import os
from datetime import datetime, timezone
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from bson.objectid import ObjectId

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
        "date_created": datetime(2025, 3, 1, 23, 45, tzinfo=timezone.utc),
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
