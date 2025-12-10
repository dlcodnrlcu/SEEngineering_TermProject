import os
from pymongo import MongoClient
from dotenv import load_dotenv

def seed_database():
    """
    Connects to the database and inserts a sample guide for the example_site.
    """
    load_dotenv()
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("DB_NAME")

    if not mongo_uri or not db_name:
        print("Error: MONGO_URI and DB_NAME must be set in your .env file.")
        return

    print(f"Connecting to MongoDB at {mongo_uri}...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    guides_collection = db.guides
    print(f"Connected to database: {db_name}")

    # Define the guide for the example site
    guide_url = "http://localhost:8000/index.html"
    
    # Check if a guide for this URL already exists
    if guides_collection.count_documents({"url": guide_url}) > 0:
        print(f"A guide for '{guide_url}' already exists. Deleting it before seeding.")
        guides_collection.delete_one({"url": guide_url})

    sample_guide = {
        "url": guide_url,
        "steps": [
            {
                "selector": "a#to-page-2",
                "action": "click",
                "description": "먼저 'Go to Page 2' 링크를 클릭하여 구독 페이지로 이동합니다."
            },
            {
                "selector": "input#email-input",
                "action": "input",
                "description": "이메일 주소를 입력하세요."
            },
            {
                "selector": "button#subscribe-btn",
                "action": "click",
                "description": "'Subscribe' 버튼을 클릭하여 구독을 완료하세요. 이제 모든 가이드가 끝났습니다!"
            }
        ],
        "name": "Sample Subscription Guide"
    }

    print("Inserting sample guide into the database...")
    result = guides_collection.insert_one(sample_guide)
    print(f"Successfully inserted guide with ID: {result.inserted_id}")
    print("Database seeding complete.")
    client.close()

if __name__ == "__main__":
    seed_database()
