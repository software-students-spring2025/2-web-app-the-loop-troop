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


def add_entry(entry):
    new_entry = {
        "date": datetime.now(timezone.utc).isoformat(),
        "content": entry,
        "tag": "Some Tag"
    }

    print(f"DEBUG: {new_entry}")

    # collection.insert_one(new_entry)

    result = collection.insert_one(new_entry)
    new_entry["_id"] = str(result.inserted_id)
    return new_entry
