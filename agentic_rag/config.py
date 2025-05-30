# config.py
import os
import json

from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        ## empty_agentic_rag_collections.py
# ========================================



CONFIG_PATH = os.path.join("agentic_rag", "vector_db_config.json")

with open(CONFIG_PATH, "r") as f:
    VECTOR_CONFIG = json.load(f)

def get_vector_config(subject_tag: str):
    return VECTOR_CONFIG.get(subject_tag.lower(), VECTOR_CONFIG["default"])




# db_config.py
# default_fallback_db = ("agentic_rag", "Misc_DB")