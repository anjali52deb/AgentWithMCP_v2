"""
🧪 STORE-Only Unit Test for Agentic-RAG System
Purpose: Validate chunking, classification, deduplication, and DB insertion
"""

import os
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agentic_rag.store_pipeline import store_multiple_files

# === CONFIG: Files for All 3 Subject Buckets ===
TEST_FILES = [
    "_Data/employee_policy.pdf",          # → Profile_DB
    "_Data/finance_policy.pdf",           # → History_DB
    "_Data/security_guidelines.pdf",      # → Misc_DB
    "_Data/random_draft.pdf",             # → Misc_DB
    "_Data/long_test_doc.txt"             # → Misc_DB
]

# === STORE TEST RUNNER ===
def run_store_only_test():
    print("\n🧪 [STORE Test] Uploading Files...")
    store_multiple_files(TEST_FILES)

if __name__ == "__main__":
    run_store_only_test()
