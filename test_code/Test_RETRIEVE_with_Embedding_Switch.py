# Test_RETRIEVE_with_Embedding_Switch.py

# ✅ Usage
# # To test with OpenAI
# python .\test_code\Test_RETRIEVE_with_Embedding_Switch.py gpt

# # To test with Google Gemini
# python .\test_code\Test_RETRIEVE_with_Embedding_Switch.py gemini


# ================ for testing =====================
# from dotenv import load_dotenv
# load_dotenv()

# import os
# print("✅ EMBEDDING_PROVIDER =", os.getenv("EMBEDDING_PROVIDER"))
# print("✅ MONGO_URI =", os.getenv("MONGO_URI"))
# ===================================================

import os
import sys

# 📁 Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agentic_rag.retrieve_pipeline import retrieve_answer

from dotenv import load_dotenv
load_dotenv()

CONFIG_PATH = "./agentic_rag/mongo_config.json"
os.environ["MONGO_CONFIG_PATH"] = CONFIG_PATH

def run_test(provider: str):
    os.environ["EMBEDDING_PROVIDER"] = provider
    print(f"\n📅 Test Run @ {get_timestamp()}")
    print(f"📁 EMBEDDING_PROVIDER = {provider.upper()}")

    # Sample queries to test
    test_cases = [
        # ("Show me the employee history for John Doe", "history"),
        # ("What is the company profile for ACME Corp?", "profile"),
        ("What is the new MongoDB index configuration update?", None)
    ]

    for i, (query, hint) in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case #{i}")
        print(f"📌 Query: {query}")
        if hint:
            print(f"📌 Subject Hint: {hint}")
        try:
            result = retrieve_answer(query, subject_hint=hint)
            print(f"✅ Response:\n{result}\n")
        except Exception as e:
            print(f"❌ ERROR: {e}\n")


def get_timestamp():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1].lower() not in ["gpt", "gemini"]:
        print("Usage: python Test_RETRIEVE_with_Embedding_Switch.py [gpt|gemini]")
        sys.exit(1)

    run_test(sys.argv[1].lower())
