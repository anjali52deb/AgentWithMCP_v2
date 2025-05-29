# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_ATLAS_URI")
VECTOR_DB_NAME = os.getenv("MONGO_DB", "agentic_rag")
VECTOR_COLLECTION = os.getenv("MONGO_COLLECTION", "vector_chunks")
LOG_DB_NAME = os.getenv("LOG_DB_NAME", "agentic_rag_logs")
