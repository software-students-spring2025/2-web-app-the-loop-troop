import pymongo
import os
from datetime import datetime, timezone
import json
from dotenv import load_dotenv
load_dotenv(override=True) 
database_url = os.getenv('MONGO_URI')
client = pymongo.MongoClient(database_url)
db = client[os.getenv("MONGO_DBNAME")]
collection = db["Users"]

def get_user(email):
    query = {"email": email}
    user = collection.find_one(query)
    return user
    if user: 
        return user
    else:
        return {"error": "Not found sorrayyy"}


