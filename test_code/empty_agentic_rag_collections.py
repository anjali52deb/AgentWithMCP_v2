## empty_agentic_rag_collections.py

"""
Safely empties selected MongoDB collections under:
- agentic_rag
- agentic_rag_logs
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# === MongoDB Setup ===
MONGO_URI = os.getenv("MONGODB_ATLAS_URI")
client = MongoClient(MONGO_URI)

# === Collections to Empty ===
collections_to_empty = {
    "agentic_rag": ["History_DB", "Misc_DB", "Profile_DB"],
    "agentic_rag_logs": ["retrieve_logs", "store_logs"]
}

# === Execution ===
for db_name, col_list in collections_to_empty.items():
    db = client[db_name]
    for col in col_list:
        result = db[col].delete_many({})
        print(f"✅ Emptied {db_name}.{col} — Deleted {result.deleted_count} documents")

print("\n✅ All listed collections have been emptied safely.")


# Run the script:
# python .\agentic_rag\empty_agentic_rag_collections.py