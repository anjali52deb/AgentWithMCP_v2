# retrieve_logger.py

"""
Handles logging for RAG Retrieve flow
Logs user query, index used, timestamp, and LLM response to Supabase
"""

import os
from supabase import create_client, Client
from agentic_rag.utils import debug_log

# Init Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_retrieve_event(log_dict: dict):
    try:
        response = supabase.table("rag_retrieve_logs").insert(log_dict).execute()
        debug_log(f"📝 Retrieve log saved: {log_dict}")
        return response
    except Exception as e:
        debug_log(f"❌ Failed to log retrieve event: {e}")
        return None
