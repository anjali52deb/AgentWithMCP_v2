
from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

# Load config and environment
load_dotenv()
MONGO_URI = os.getenv("MONGODB_ATLAS_URI")

client = MongoClient(MONGO_URI)
# config_path = Path("vector_db_config.json")
config_path = Path(__file__).parent / "vector_db_config.json"
with open(config_path, "r") as f:
    config = json.load(f)


def deduplicate_chunks():
    print("\n🔁 De-duplicating knowledge chunk collections...")
    for label, entry in config.items():
        if label == "logs":
            continue  # Skip logs in this function

        db_name = entry["db_name"]
        coll_name = entry["collection_name"]
        collection = client[db_name][coll_name]

        print(f"🧠 Checking: {db_name}.{coll_name} ({label})")

        pipeline = [
            {
                "$group": {
                    "_id": "$metadata.chunk_hash",
                    "ids": {"$addToSet": "$_id"},
                    "count": {"$sum": 1}
                }
            },
            {"$match": {"count": {"$gt": 1}}}
        ]

        duplicates = list(collection.aggregate(pipeline))
        total_removed = 0

        for group in duplicates:
            keep = group["ids"][0]
            to_delete = group["ids"][1:]
            collection.delete_many({"_id": {"$in": to_delete}})
            total_removed += len(to_delete)

        print(f"   ✅ Removed {total_removed} duplicate chunks")


def deduplicate_logs():
    print("\n🧹 De-duplicating log entries (based on file_hash)...")
    logs = config.get("logs", {})
    db_name = logs.get("db_name")
    log_targets = [("store_logs", logs.get("store_logs")), ("retrieve_logs", logs.get("retrieve_logs"))]

    for label, coll_name in log_targets:
        if not coll_name:
            continue
        collection = client[db_name][coll_name]
        print(f"📝 Checking: {db_name}.{coll_name} ({label})")

        pipeline = [
            {
                "$group": {
                    "_id": "$file_hash",
                    "ids": {"$addToSet": "$_id"},
                    "count": {"$sum": 1}
                }
            },
            {"$match": {"count": {"$gt": 1}}}
        ]

        duplicates = list(collection.aggregate(pipeline))
        total_removed = 0

        for group in duplicates:
            keep = group["ids"][0]
            to_delete = group["ids"][1:]
            collection.delete_many({"_id": {"$in": to_delete}})
            total_removed += len(to_delete)

        print(f"   ✅ Removed {total_removed} duplicate log entries")


# Run both dedup routines
if __name__ == "__main__":
    deduplicate_chunks()
    deduplicate_logs()
