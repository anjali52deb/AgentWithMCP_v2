# TestAgenticRAG.py

"""
Test script for validating Agentic-RAG pipeline with both GPT and Gemini:
1. Store with GPT
2. Store with Gemini
3. Retrieve HR query using GPT
4. Retrieve HR query using Gemini
5. Retrieve Finance query using GPT
6. Retrieve Finance query using Gemini
"""

from routes.agentic_rag_pipeline import store_document, retrieve_answer
import os

# Setup env (replace with real secrets or load from .env)
os.environ["PINECONE_API_KEY"] = "your-pinecone-key"
os.environ["OPENAI_API_KEY"] = "your-openai-key"
os.environ["GOOGLE_API_KEY"] = "your-gemini-key"
os.environ["SUPABASE_URL"] = "your-supabase-url"
os.environ["SUPABASE_KEY"] = "your-supabase-key"

FILE_PATH = "data/leave_policy.pdf"
INDEX_NAME = "rag_hr_policy"

# --- STORE Tests ---
def test_store_with_gpt():
    print("\n📥 Store with GPT")
    store_document(FILE_PATH, INDEX_NAME, llm_type="gpt")

def test_store_with_gemini():
    print("\n📥 Store with Gemini")
    store_document(FILE_PATH, INDEX_NAME, llm_type="gemini")

# --- RETRIEVE Tests ---
def test_retrieve_hr_with_gpt():
    print("\n🔍 Retrieve HR Query with GPT")
    retrieve_answer("What is the paid leave policy?", INDEX_NAME, llm_type="gpt")

def test_retrieve_hr_with_gemini():
    print("\n🔍 Retrieve HR Query with Gemini")
    retrieve_answer("What is the paid leave policy?", INDEX_NAME, llm_type="gemini")

def test_retrieve_finance_with_gpt():
    print("\n💼 Retrieve Finance Query with GPT")
    retrieve_answer("What is the Q1 revenue?", "rag_finance", llm_type="gpt")

def test_retrieve_finance_with_gemini():
    print("\n💼 Retrieve Finance Query with Gemini")
    retrieve_answer("What is the Q1 revenue?", "rag_finance", llm_type="gemini")

# --- MAIN RUNNER ---
if __name__ == "__main__":
    test_store_with_gpt()
    test_store_with_gemini()
    test_retrieve_hr_with_gpt()
    test_retrieve_hr_with_gemini()
    test_retrieve_finance_with_gpt()
    test_retrieve_finance_with_gemini()
