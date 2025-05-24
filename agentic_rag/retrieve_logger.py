# retrieve_logger.py

from pymongo import MongoClient
from datetime import datetime
from agentic_rag.config import MONGO_URI, LOG_DB_NAME

def log_retrieve_event(query, result_count, source_index, llm_used, response_summary=None):
    client = MongoClient(MONGO_URI)
    db = client[LOG_DB_NAME]
    collection = db["retrieve_logs"]

    entry = {
        "query": query,
        "result_count": result_count,
        "source_index": source_index,
        "llm_used": llm_used,
        "timestamp": datetime.utcnow()
    }

    if response_summary:
        entry["response_summary"] = response_summary

    collection.insert_one(entry)
    print(f"📝 Logged RETRIEVE event for: '{query}'")
