# store_index_utils.py

from pymongo import MongoClient
import os
from datetime import datetime

MONGO_URI = os.getenv("MONGODB_ATLAS_URI")

def ensure_collection_exists(db_name: str, collection_name: str):
    client = MongoClient(MONGO_URI)
    db = client[db_name]

    if collection_name not in db.list_collection_names():
        print(f"⚠️ Collection '{collection_name}' does not exist. Creating dummy document...")
        db[collection_name].insert_one({
            "_meta": "trigger_index",
            "created_at": datetime.utcnow()
        })
        print(f"✅ Dummy document inserted into '{collection_name}'.")

    else:
        print(f"✅ Collection '{collection_name}' already exists.")
