# TestAgenticRAG.py

"""
Test runner for modular Agentic-RAG system
Covers Store + Retrieve with GPT and Gemini
"""

from agentic_rag.master_rag_agent import run_master_agent
import os

# Setup environment (you can also use dotenv)
os.environ["PINECONE_API_KEY"] = "your-pinecone-key"
os.environ["OPENAI_API_KEY"] = "your-openai-key"
os.environ["GOOGLE_API_KEY"] = "your-gemini-key"
os.environ["SUPABASE_URL"] = "your-supabase-url"
os.environ["SUPABASE_KEY"] = "your-supabase-key"

# File for storing
FILE_PATH = "data/leave_policy.pdf"

# Test Scenarios

def test_store_with_gpt():
    print("\n--- Test: Store Document with GPT ---")
    run_master_agent(input_data=FILE_PATH, is_file=True, llm_type="gpt", temperature=0.2, debug=True)

def test_store_with_gemini():
    print("\n--- Test: Store Document with Gemini ---")
    run_master_agent(input_data=FILE_PATH, is_file=True, llm_type="gemini", temperature=0.2, debug=True)

def test_retrieve_hr_with_gpt():
    print("\n--- Test: Retrieve HR Info with GPT ---")
    run_master_agent(input_data="What is the leave policy?", is_file=False, llm_type="gpt", temperature=0.3, debug=True)

def test_retrieve_hr_with_gemini():
    print("\n--- Test: Retrieve HR Info with Gemini ---")
    run_master_agent(input_data="What is the leave policy?", is_file=False, llm_type="gemini", temperature=0.3, debug=True)

def test_retrieve_finance_with_gpt():
    print("\n--- Test: Retrieve Finance Info with GPT ---")
    run_master_agent(input_data="Tell me Q1 financial summary", is_file=False, llm_type="gpt", temperature=0.3, debug=True)

def test_retrieve_finance_with_gemini():
    print("\n--- Test: Retrieve Finance Info with Gemini ---")
    run_master_agent(input_data="Tell me Q1 financial summary", is_file=False, llm_type="gemini", temperature=0.3, debug=True)

# Run All
if __name__ == "__main__":
    test_store_with_gpt()
    test_store_with_gemini()
    test_retrieve_hr_with_gpt()
    test_retrieve_hr_with_gemini()
    test_retrieve_finance_with_gpt()
    test_retrieve_finance_with_gemini()
