# TestAgenticRAG.py

"""
Test runner for modular Agentic-RAG system
Covers Store + Retrieve with GPT and Gemini
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from agentic_rag.store_pipeline import store_document


# Set test file path (adjust as needed)
FILE_PATH = r"_Data/HR_Policy_Handbook.pdf"  # or "data/HR_Policy_Handbook.pdf"

# Set keys from environment (safe fallback)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Confirm environment
print("\n🧪 STORE FLOW TEST STARTED")
print("📂 File to process:", FILE_PATH)
print("🔐 Pinecone Key Present:", bool(PINECONE_API_KEY))
print("🔐 OpenAI Key Present:", bool(OPENAI_API_KEY))
print("🔐 Supabase URL Present:", bool(SUPABASE_URL))
print("🔐 Supabase Key Present:", bool(SUPABASE_KEY))

# Execute store pipeline
store_document(
    filepath=FILE_PATH,
    llm_type="gpt",
    temperature=0.2,
    debug=True
)

print("\n✅ STORE FLOW TEST COMPLETE")
