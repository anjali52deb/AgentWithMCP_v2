import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from agentic_rag.store_pipeline import store_multiple_files
from agentic_rag.retrieve_router import retrieve_answer

from Old_Test_Files.Test_view_logs import view_last_logs
from Old_Test_Files.Test_rag_quality import test_chunk_sizes, test_embedding_models, batch_store_retrieve, export_csv

FILE_LIST = [
    r"_Data/employee_policy.pdf",
    r"_Data/finance_policy.pdf",
    r"_Data/security_guidelines.pdf"
]

QUERIES = [
    "What is our HR policy on sick leave?",
    "What’s the latest transaction history for Q1?"
]

def menu():
    print("""
🧪 UNIFIED AGENTIC-RAG TEST MENU
1. Multi-file STORE test (subject-based routing)
2. RETRIEVE test (predefined queries)
3. View last RETRIEVE logs
4. RAG Quality → Test Multiple Chunk Sizes
5. RAG Quality → Test Multiple Embedding Models
6. RAG Quality → Batch Queries Test
7. Export RAG Quality Results to CSV
0. Exit
""")
    return input("Choose an option [0-7]: ").strip()

def run():
    while True:
        choice = menu()

        if choice == "1":
            print("\n📂 Running multi-file STORE test...")
            store_multiple_files(FILE_LIST, tag="auto")

        elif choice == "2":
            print("\n🔎 Running predefined RETRIEVE test queries...")
            for q in QUERIES:
                print(f"\n🔹 Query: {q}")
                print(retrieve_answer(q))

        elif choice == "3":
            view_last_logs(log_type="retrieve", limit=10)

        elif choice == "4":
            test_chunk_sizes()

        elif choice == "5":
            test_embedding_models()

        elif choice == "6":
            batch_store_retrieve()

        elif choice == "7":
            export_csv()

        elif choice == "0":
            print("👋 Exiting unified tester.")
            break

        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    run()
