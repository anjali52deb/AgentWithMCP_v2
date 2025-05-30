
"""
Automated Unit Test Script for Agentic-RAG System
Tests: STORE, RETRIEVE, Routing, Logging, Deduplication
"""

import os
from store_pipeline import store_multiple_files
from retrieve_pipeline import retrieve_with_llm
from mongo_client import get_mongo_client
from logger import log_store_event, log_retrieve_event
from subject_db_mapper import get_db_and_collection_for_subject
from utils import compute_md5

# === CONFIG ===
TEST_FILES = [
    "_Data/employee_policy.pdf",     # Should go to Profile_DB
    "_Data/finance_policy.pdf",      # Should go to History_DB
    "_Data/security_guidelines.pdf"  # Should default to Misc_DB
]

TEST_QUERIES = [
    "What is our HR policy on sick leave?",                 # Target Profile_DB
    "What's the budget approval process in finance?",       # Target History_DB
    "Summarize this uploaded security file."                # Likely Misc_DB fallback
]

# === TEST RUNNER ===
def run_selected_tests():
    print("\n🧪 Starting Unit Tests for Agentic-RAG...")

    # --- Test 1: STORE flow
    print("\n📂 [Test] Multi-file STORE Flow")
    store_multiple_files(TEST_FILES)

    # --- Test 2: Deduplication (re-upload)
    print("\n📁 [Test] Deduplication (Re-upload same files)")
    store_multiple_files(TEST_FILES)

    # --- Test 3: RETRIEVE flow
    print("\n🔎 [Test] RETRIEVE Queries")
    for query in TEST_QUERIES:
        print(f"\n💬 Query: {query}")
        retrieve_with_llm(query)

    # --- Test 4: Subject → Collection Mapping
    print("\n📊 [Test] Subject-to-DB Mapping Check")
    for file_path in TEST_FILES:
        subject = os.path.basename(file_path).split("_")[0]
        db, coll = get_db_and_collection_for_subject(subject)
        print(f"📌 File: {file_path} → DB: {db}, Collection: {coll}")

    # --- Test 5: Manual Log Dedup Check
    print("\n🧾 [Test] Log Metadata Check (file_hash)")
    mongo = get_mongo_client()
    for file_path in TEST_FILES:
        file_hash = compute_md5(file_path)
        result = mongo["agentic_rag"]["logs"].find_one({"metadata.file_hash": file_hash})
        print(f"🔍 Hash: {file_hash} → {'Found' if result else 'Not Found'}")

    print("\n✅ All selected tests completed.")

if __name__ == "__main__":
    run_selected_tests()
