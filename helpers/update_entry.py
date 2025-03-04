import os
from pymongo import MongoClient
from bson.objectid import ObjectId
database_url = os.getenv('MONGO_URI')
client = MongoClient(database_url)
db = client[os.getenv("MONGO_DBNAME")]
collection = db["journalEntries"]

def update_entry(entryId, content):
    query = {"_id": ObjectId(entryId)}
    update = {"$set": {"content": content}}
    collection.update_one(query, update)

