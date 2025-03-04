import pymongo
import os
from datetime import datetime, timezone

database_url = os.getenv('MONGO_URI')
client = pymongo.MongoClient(database_url)
db = client[os.getenv("MONGO_DBNAME")]
collection = db["journalEntries"]

def get_all_entries():
    entries = collection.find()

    return entries