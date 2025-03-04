import os
from pymongo import MongoClient
from bson.objectid import ObjectId
database_url = os.getenv('MONGO_URI')
client = MongoClient(database_url)
db = client[os.getenv("MONGO_DBNAME")]
collection = db["journalEntries"]

def update_entry(entryId, content, username):
    existing_entry = collection.find_one({"_id": ObjectId(entryId)})


    old_word_count = existing_entry["word_count"]
    new_word_count = len(content.split())
    word_diff = new_word_count - old_word_count 

    query = {"_id": ObjectId(entryId)}
    update = {
        "$set": {
            "content": content,
            "word_count": new_word_count
        }
    }
    result = collection.update_one(query, update)

    if result.modified_count > 0:
        # Adjust total words in user stats
        db.users.update_one(
            {"username": username},
            {"$inc": {"user_stats.total_words": word_diff}}
        )
        return True  # successfully updated
    else:
        return False  # failed to update

