# store_logger.py

from pymongo import MongoClient
from datetime import datetime
from agentic_rag.config import MONGO_URI, LOG_DB_NAME

def log_store_event(file_name, chunk_count, status, file_hash=None, additional_info=None):
    client = MongoClient(MONGO_URI)
    db = client[LOG_DB_NAME]
    collection = db["store_logs"]

    log_entry = {
        "file_name": file_name,
        "chunk_count": chunk_count,
        "status": status,
        "timestamp": datetime.utcnow()
    }

    if file_hash:
        log_entry["file_hash"] = file_hash

    if additional_info:
        log_entry.update(additional_info)

    collection.insert_one(log_entry)
    print(f"📝 Logged STORE event for: {file_name}")





# # store_logger.py

# from pymongo import MongoClient
# from datetime import datetime
# from agentic_rag.config import MONGO_URI, LOG_DB_NAME

# def log_store_event(file_name, chunk_count, status, additional_info=None):
#     client = MongoClient(MONGO_URI)
#     db = client[LOG_DB_NAME]
#     collection = db["store_logs"]

#     log_entry = {
#         "file_name": file_name,
#         "chunk_count": chunk_count,
#         "status": status,
#         "timestamp": datetime.utcnow()
#     }

#     if additional_info:
#         log_entry.update(additional_info)

#     collection.insert_one(log_entry)
#     print(f"📝 Logged STORE event for: {file_name}")
