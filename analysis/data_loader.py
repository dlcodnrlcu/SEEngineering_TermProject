import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import pandas as pd

def load_data_from_db():
    """
    Connects to the MongoDB database and loads the event logs into a pandas DataFrame.
    """
    load_dotenv('../server/.env')  # Assuming .env is in the server directory
    MONGO_URI = os.getenv("MONGO_URI")

    if not MONGO_URI:
        print("MONGO_URI not found. Make sure it's set in server/.env")
        return None

    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ismaster')
        db = client.followme_db
        print("MongoDB connection successful.")
    except ConnectionFailure:
        print("MongoDB connection failed.")
        return None

    # Load data from the event_logs collection
    logs = list(db.event_logs.find())
    
    if not logs:
        print("No logs found in the database.")
        return pd.DataFrame()

    df = pd.DataFrame(logs)
    print(f"Loaded {len(df)} logs into DataFrame.")
    
    # Basic preprocessing: convert timestamp to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    return df

if __name__ == '__main__':
    df_logs = load_data_from_db()
    if df_logs is not None:
        print("DataFrame head:")
        print(df_logs.head())
