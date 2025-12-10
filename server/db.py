import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    db = client.followme_db
except ConnectionFailure:
    print("MongoDB connection failed")
    db = None

def insert_logs(logs):
    """
    Inserts a batch of logs into the event_logs collection.
    """
    if db is not None:
        try:
            return db.event_logs.insert_many(logs)
        except Exception as e:
            print(f"An error occurred while inserting logs: {e}")
            return None
    else:
        print("Cannot insert logs, database connection not available.")
        return None

def get_guide_for_url(url):
    """
    Retrieves a guide for a specific URL from the analyzed_guides collection.
    """
    if db is not None:
        try:
            return db.analyzed_guides.find_one({"url": url})
        except Exception as e:
            print(f"An error occurred while fetching the guide: {e}")
            return None
    else:
        print("Cannot get guide, database connection not available.")
        return None
