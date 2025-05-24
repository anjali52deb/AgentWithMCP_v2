# log_metadata_reader.py

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


# # log_metadata_reader.py

# from pymongo import MongoClient
# from agentic_rag.config import MONGO_URI, LOG_DB_NAME

# def file_already_stored(file_name: str) -> bool:
#     """
#     Checks if a file with the given name has already been logged in store_logs.
#     """
#     client = MongoClient(MONGO_URI)
#     db = client[LOG_DB_NAME]
#     collection = db["store_logs"]

#     result = collection.find_one({"file_name": file_name})
#     return result is not None
