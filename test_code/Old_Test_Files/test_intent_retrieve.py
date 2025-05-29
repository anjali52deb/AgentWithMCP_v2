import sys
import os
from dotenv import load_dotenv
from pprint import pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from agentic_rag.retrieve_router import retrieve_answer

queries = [
    "What is our HR policy on sick leave?",
    "Tell me a joke.",
    "Can you summarize this PDF?",
    "What’s the latest transaction history for Q1?"
]

for q in queries:
    print(f"\n🔹 Query: {q}")
    print(retrieve_answer(q))
