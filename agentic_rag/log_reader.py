# log_metadata_reader.py
# log_viewer.py

from datetime import datetime
import argparse
from pprint import pprint
from pymongo import MongoClient
from agentic_rag.config import MONGO_URI, LOG_DB_NAME


def file_already_stored(file_name: str) -> bool:
    client = MongoClient(MONGO_URI)
    db = client[LOG_DB_NAME]
    collection = db["store_logs"]
    result = collection.find_one({"file_name": file_name})
    return result is not None

def file_hash_already_stored(file_hash: str) -> bool:
    client = MongoClient(MONGO_URI)
    db = client[LOG_DB_NAME]
    collection = db["store_logs"]
    result = collection.find_one({"file_hash": file_hash})
    return result is not None

def get_collection(log_type):
    client = MongoClient(MONGO_URI)
    db = client[LOG_DB_NAME]
    if log_type == "store":
        return db["store_logs"]
    elif log_type == "retrieve":
        return db["retrieve_logs"]
    else:
        raise ValueError("Invalid log type. Use 'store' or 'retrieve'.")

def view_logs(log_type, limit=10, file_name=None, query=None, from_date=None, to_date=None):
    collection = get_collection(log_type)

    filter_query = {}

    if file_name and log_type == "store":
        filter_query["file_name"] = file_name

    if query and log_type == "retrieve":
        filter_query["query"] = {"$regex": query, "$options": "i"}

    if from_date or to_date:
        timestamp_filter = {}
        if from_date:
            timestamp_filter["$gte"] = datetime.fromisoformat(from_date)
        if to_date:
            timestamp_filter["$lte"] = datetime.fromisoformat(to_date)
        filter_query["timestamp"] = timestamp_filter

    logs = collection.find(filter_query).sort("timestamp", -1).limit(limit)

    print(f"\n🔍 Showing latest {limit} '{log_type}' log(s):")
    for log in logs:
        log.pop("_id", None)
        pprint(log)
        print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description="Agentic-RAG MongoDB Log Viewer")
    parser.add_argument("--type", choices=["store", "retrieve"], required=True, help="Log type to view")
    parser.add_argument("--limit", type=int, default=10, help="How many logs to fetch")
    parser.add_argument("--file", help="Filter by file name (store logs only)")
    parser.add_argument("--query", help="Filter by query text (retrieve logs only)")
    parser.add_argument("--from_date", help="Filter from date (YYYY-MM-DD format)")
    parser.add_argument("--to_date", help="Filter to date (YYYY-MM-DD format)")

    args = parser.parse_args()

    view_logs(
        log_type=args.type,
        limit=args.limit,
        file_name=args.file,
        query=args.query,
        from_date=args.from_date,
        to_date=args.to_date
    )

if __name__ == "__main__":
    main()
