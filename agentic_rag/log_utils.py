# log_utils.py

import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

LOG_DB = os.getenv("LOG_DB", "agentic_rag_logs")
LOG_COLLECTION = os.getenv("RETRIEVE_LOG_COLLECTION", "retrieve_logs")
MONGO_URI = os.getenv("MONGO_URI")

def log_retrieve_event(query: str, subject: str, match_count: int, provider: str):
    client = MongoClient(MONGO_URI)
    db = client[LOG_DB]
    collection = db[LOG_COLLECTION]

    log_doc = {
        "query": query,
        "subject": subject,
        "matches_found": match_count,
        "provider": provider,
        "timestamp": datetime.utcnow(),
        "pipeline_version": os.getenv("RETRIEVE_PIPELINE_VERSION", "v1.0")
    }

    collection.insert_one(log_doc)


def read_retrieve_logs(limit: int = 10):
    """Read the latest N retrieve logs (default: 10)."""
    client = MongoClient(MONGO_URI)
    db = client[LOG_DB]
    collection = db[LOG_COLLECTION]

    return list(collection.find().sort("timestamp", -1).limit(limit))

def purge_old_logs(cutoff_datetime):
    """Delete logs older than the given datetime."""
    client = MongoClient(MONGO_URI)
    db = client[LOG_DB]
    collection = db[LOG_COLLECTION]

    result = collection.delete_many({"timestamp": {"$lt": cutoff_datetime}})
    print(f"[LOG CLEANUP] Deleted {result.deleted_count} logs older than {cutoff_datetime}")


def purge_old_retrieve_logs(days: int = 1):
    """Deletes retrieve logs older than the specified number of days (default: 1)."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    purge_old_logs(cutoff)



_last_cleanup_date = None

def clean_logs_once_per_day():
    """Cleans logs only once per UTC day (no matter how many times retrieve runs)."""
    global _last_cleanup_date

    today = datetime.utcnow().date()
    if _last_cleanup_date != today:
        print("[LOG CLEANUP] Running daily retrieve log cleanup...")
        purge_old_retrieve_logs()
        _last_cleanup_date = today
    else:
        print("[LOG CLEANUP] Skipped (already cleaned today)")
