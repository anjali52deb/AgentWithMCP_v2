# 🧪 How to Use
# ✅ Option 1: Use .env (default)
#     EMBEDDING_PROVIDER=gpt
#     python Test_STORE_with_Embedding_Switch.py

# ✅ Option 2: Command-line override
    # python .\test_code\Test_STORE_with_Embedding_Switch.py gemini
    # python .\test_code\Test_STORE_with_Embedding_Switch.py gpt


import os
import sys
import traceback
from datetime import datetime

# 📁 Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agentic_rag.store_pipeline import store_pipeline

# ✅ Test file paths (use relative paths inside '_Data' folder)
TEST_FILES = [
    "profile_testfile.txt",
    "history_transactions.csv",
    "misc_notes.txt",
    "history.pdf",
    "Product_FAQ.txt"
]

USER_ID = "test_user"
BASE_DIR = "./_Data"
CONFIG_PATH = "./agentic_rag/mongo_config.json"

# Allow manual override via command-line arg or fallback to .env
def get_provider():
    if len(sys.argv) > 1:
        return sys.argv[1].lower()
    return os.getenv("EMBEDDING_PROVIDER", "gpt").lower()

def log_step(step: str):
    print("\n" + ">>>" * 10 + f" {step} " + "<<<" * 10)

def test_store_block(file_path, user_id):
    log_step(f"START TEST: {os.path.basename(file_path)}")
    try:
        store_pipeline(file_path=file_path, user_id=user_id, config_path=CONFIG_PATH)
        log_step("✅ COMPLETED: STORE & LOG")
    except Exception as e:
        print(f"❌ Exception during STORE pipeline for {file_path}: {e}")
        traceback.print_exc()
        log_step("💥 FAILED")

def run_test():
    provider = get_provider()
    os.environ["EMBEDDING_PROVIDER"] = provider  # force override for pipeline
    print(f"📅 Test Run @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 EMBEDDING_PROVIDER = {provider}")
    print(f"📁 Found {len(TEST_FILES)} test files to process\n")

    for fname in TEST_FILES:
        file_path = os.path.join(BASE_DIR, fname)
        if not os.path.isfile(file_path):
            print(f"⚠️  File not found, skipping: {file_path}")
            continue
        test_store_block(file_path, USER_ID)

if __name__ == "__main__":
    run_test()
