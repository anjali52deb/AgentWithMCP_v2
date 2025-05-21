# store_logger.py

"""
Handles logging for RAG Store flow
Logs file ingestion metadata to Supabase or other tracking DB
"""

from agentic_rag.utils import debug_log
import os
from supabase import create_client, Client

# Init Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def log_store_event(log_dict: dict):
    try:
        response = supabase.table("rag_store_logs").insert(log_dict).execute()
        debug_log(f"📝 Store metadata logged: {log_dict}")
        return response
    except Exception as e:
        debug_log(f"❌ Failed to log store metadata: {e}")
        return None
