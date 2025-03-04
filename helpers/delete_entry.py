import os
from dotenv import load_dotenv, dotenv_values
from pymongo import MongoClient
from bson.objectid import ObjectId
load_dotenv(override=True)
database_url = os.getenv('MONGO_URI')
client = MongoClient(database_url)


db = client[os.getenv("MONGO_DBNAME")]
collection = db["journalEntries"]

# def delete_entry(id):
#     query = {"_id": ObjectId(id)}
#     entry = collection.delete_one(query)
#     print(entry)

def delete_entry(entry_id, username):
    """Deletes an entry by ID and returns whether it was successful."""
    try:
        if not entry_id:
            raise ValueError("Invalid entry ID")
        
        entry = collection.find_one({"_id": ObjectId(entry_id)})
        word_count = entry["word_count"]

        query = {"_id": ObjectId(entry_id)}
        result = collection.delete_one(query)

        if result.deleted_count > 0:
            # decrement total_words and total_entries
            db.users.update_one(
                {"username": username},
                {"$inc": {
                    "user_stats.total_words": -word_count,
                    "user_stats.total_entries": -1
                }}
            )
            return True  # successfully deleted
        else:
            return False  # entry was not deleted

    except Exception as e:
        print(f"Error deleting entry: {e}")
        return False  # Indicate failure

