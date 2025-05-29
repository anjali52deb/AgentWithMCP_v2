# retrieve_logger.py

from pymongo import MongoClient
from datetime import datetime
from agentic_rag.config import MONGO_URI, LOG_DB_NAME

import os

client = MongoClient(os.getenv("MONGODB_ATLAS_URI"))
log_collection = client["agentic_rag"]["retrieve_logs"]

def log_retrieve_event(query, intent, subject, db_name, result_count):
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": "retrieve",
        "query": query,
        "intent": intent,
        "subject": subject,
        "collection": db_name,
        "results_found": result_count
    }
    log_collection.insert_one(log)
    print(f"📝 Logged RETRIEVE event for query: {query}")


# def log_retrieve_event(query, result_count, source_index, llm_used, response_summary=None):
#     client = MongoClient(MONGO_URI)
#     db = client[LOG_DB_NAME]
#     collection = db["retrieve_logs"]

#     entry = {
#         "query": query,
#         "result_count": result_count,
#         "source_index": source_index,
#         "llm_used": llm_used,
#         "timestamp": datetime.utcnow()
#     }

#     if response_summary:
#         entry["response_summary"] = response_summary

#     collection.insert_one(entry)
#     print(f"📝 Logged RETRIEVE event for: '{query}'")
