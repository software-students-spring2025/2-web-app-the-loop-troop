import os
from pymongo import MongoClient
from bson.objectid import ObjectId
database_url = os.getenv('MONGO_URI')
client = MongoClient(database_url)
db = client[os.getenv("MONGO_DBNAME")]
collection = db["journalEntries"]

def get_entry(entryId):
    query = {"_id": ObjectId(entryId)}
    result = collection.find_one(query)
    return result

