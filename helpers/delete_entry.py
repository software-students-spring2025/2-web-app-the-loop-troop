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

def delete_entry(entry_id):
    """Deletes an entry by ID and returns whether it was successful."""
    try:
        if not entry_id:
            raise ValueError("Invalid entry ID")

        query = {"_id": ObjectId(entry_id)}
        result = collection.delete_one(query)

        return result.deleted_count > 0  # Returns True if deleted, False if not found

    except Exception as e:
        print(f"Error deleting entry: {e}")
        return False  # Indicate failure

