import os
from dotenv import load_dotenv
import pymongo
from bson.objectid import ObjectId

load_dotenv(override=True)
database_url = os.getenv('MONGO_URI')
client = pymongo.MongoClient(database_url)
db = client[os.getenv("MONGO_DBNAME")]
collection = db["journalEntries"]

def share_entry(entry_id, username):
    try:
        # check if entry exists and belongs to the user
        entry = collection.find_one({"_id": ObjectId(entry_id), "username": username})
        if not entry:
            return False, "Entry not found or not owned by you."
        
        # update entry to mark as shared
        result = collection.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": {"is_shared": True}}
        )
        if result.modified_count > 0:
            return True, "Entry shared successfully."
        else:
            return False, "Failed to share the entry."
    except Exception as e:
        return False, str(e)
