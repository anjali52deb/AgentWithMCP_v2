# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_ATLAS_URI")
VECTOR_DB_NAME = os.getenv("MONGO_DB", "agentic_rag")
VECTOR_COLLECTION = os.getenv("MONGO_COLLECTION", "vector_chunks")
LOG_DB_NAME = os.getenv("LOG_DB_NAME", "agentic_rag_logs")

# ========================================
# ADD all other KEYS later such as .... and REDER THIS WAY >>> from agentic_rag.config import * (or call relevant)
        # index_manager.py
        # intent_classifier.py
        # mongo_client.py
        # store_index_utils.py
        # subject_classifier.py
        # subject_db_mapper.py

# ========================================

# db_config.py
default_fallback_db = ("agentic_rag", "Misc_DB")
