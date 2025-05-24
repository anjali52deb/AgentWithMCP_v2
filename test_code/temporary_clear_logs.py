# temporary_clear_logs.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from agentic_rag.config import MONGO_URI, LOG_DB_NAME

client = MongoClient(MONGO_URI)
db = client[LOG_DB_NAME]
deleted = db["store_logs"].delete_many({"file_name": "HR_Policy_Handbook.pdf"})
print(f"Deleted {deleted.deleted_count} old logs.")
