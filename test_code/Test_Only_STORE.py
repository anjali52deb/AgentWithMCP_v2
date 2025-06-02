import os
import sys
import traceback
from datetime import datetime

# 📁 Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agentic_rag.store_pipeline import store_pipeline

# ✅ Test file paths (use relative paths inside 'test_files' folder)
TEST_FILES = [
    "profile_testfile.txt",
    "history_transactions.csv",
    "misc_notes.txt"
]

# TEST_FILES = [
#     "profile.pdf",
#     "history.pdf",
#     "security_guidelines.pdf"
#     # "random_draft.pdf",  # ✅ Newly added
#     # "long_test_doc.txt"
# ]

USER_ID = "test_user"
BASE_DIR = "./_Data"
CONFIG_PATH = "./agentic_rag/mongo_config.json"


def log_step(step: str):
    print("\n" + ">>>" * 10 + f" {step} " + "<<<" * 10)


def test_store_block(file_path, user_id):
    log_step(f"START TEST: {os.path.basename(file_path)}")
    try:
        store_pipeline(file_path=file_path, user_id=USER_ID, config_path=CONFIG_PATH)

        log_step("✅ COMPLETED: STORE & LOG")
    except Exception as e:
        print(f"❌ Exception during STORE pipeline for {file_path}: {e}")
        traceback.print_exc()
        log_step("💥 FAILED")


def run_test():
    all_files = [os.path.join(BASE_DIR, f) for f in TEST_FILES]
    print(f"\n📅 Test Run @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Found {len(all_files)} test files to process\n")

    for file_path in all_files:
        if not os.path.isfile(file_path):
            print(f"⚠️  File not found, skipping: {file_path}")
            continue
        test_store_block(file_path, USER_ID)


if __name__ == "__main__":
    run_test()