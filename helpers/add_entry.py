import pymongo
import os
from dotenv import load_dotenv
load_dotenv(override=True) 
from datetime import datetime, timezone
import json

database_url = os.getenv('MONGO_URI')
client = pymongo.MongoClient(database_url)
db = client[os.getenv("MONGO_DBNAME")]
collection = db["journalEntries"]


def add_entry(entry, username):
    word_count = len(entry.split())

    new_entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "content": entry,
        "tag": "Some Tag",
        "username": username,
        "word_count": word_count,
        "date_created": datetime.now(timezone.utc),
        "is_shared": False
    }

    print(f"DEBUG: {new_entry}")

    # collection.insert_one(new_entry)

    result = collection.insert_one(new_entry)
    new_entry["_id"] = str(result.inserted_id)

    # increment user_stats in the database
    db.users.update_one(
        {"username": username},
        {"$inc": {
            "user_stats.total_words": word_count,
            "user_stats.total_entries": 1
        }}
    )

    return new_entry
