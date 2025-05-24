# Test_AgenticRAG.py

"""
Unified test runner for Agentic-RAG system
Scenarios:
1. Store file and log
2. View store logs
3. Run a retrieve query
4. View retrieve logs
"""

import sys
import os
from dotenv import load_dotenv
from pprint import pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

# ✅ MODULES
from agentic_rag.store_pipeline import store_to_mongodb
from agentic_rag.log_viewer import view_logs
from agentic_rag.retrieve_pipeline import retrieve_from_mongodb
from agentic_rag.master_rag_agent import route_mode

# ✅ CONFIGS
FILE_PATH = r"_Data/HR_Policy_Handbook.pdf"
RETRIEVE_QUERY = "What is the leave policy?"
RETRIEVE_TAG = "vector_index"

# ✅ MENU
def main():
    print("\n🧪 Agentic-RAG Test Console")
    print("1️⃣  Run STORE pipeline")
    print("2️⃣  View STORE logs")
    print("3️⃣  Run RETRIEVE query")
    print("4️⃣  View RETRIEVE logs")
    print("0️⃣  Exit")

    choice = input("\nChoose a test [0–4]: ").strip()

    if choice == "1":
        print(f"\n📂 Processing file: {FILE_PATH}")

        result = route_mode("store", FILE_PATH)
        print(result)

    elif choice == "2":
        print("\n📜 Showing STORE logs:")
        view_logs(log_type="store", limit=5)
    elif choice == "3":
        print(f"\n❓ Query: {RETRIEVE_QUERY}")
        answer = retrieve_from_mongodb(RETRIEVE_QUERY, tag=RETRIEVE_TAG)
        print("\n💡 Answer:\n", answer)
    elif choice == "4":
        print("\n📜 Showing RETRIEVE logs:")
        view_logs(log_type="retrieve", limit=5)
    elif choice == "0":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice. Try again.")

    print("\n🔁 Back to menu...\n")
    main()


if __name__ == "__main__":
    main()


# 🧪 Agentic-RAG Test Console
# 1️⃣  Run STORE pipeline
# 2️⃣  View STORE logs
# 3️⃣  Run RETRIEVE query
# 4️⃣  View RETRIEVE logs
# 0️⃣  Exit

# Choose a test [0–4]:
