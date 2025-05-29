# view_logs.py

from pymongo import MongoClient
import os
from pprint import pprint

client = MongoClient(os.getenv("MONGODB_ATLAS_URI"))
log_collection = client["agentic_rag"]["retrieve_logs"]

def view_last_logs(log_type="retrieve", limit=10):
    print(f"\n📜 Showing last {limit} {log_type.upper()} logs:\n{'-'*60}")
    # logs = log_collection.find({"type": log_type}).sort("timestamp", -1).limit(limit)
    logs = log_collection.find().sort("timestamp", -1).limit(10)
    
    for log in logs:
        pprint(log)
        print("-" * 60)

if __name__ == "__main__":
    view_last_logs()
