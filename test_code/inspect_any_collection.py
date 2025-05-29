from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_ATLAS_URI"))

db = client["agentic_rag"]
collection_name = input("🔍 Enter collection to inspect (e.g. Misc_DB): ").strip()
collection = db[collection_name]

print(f"\n📂 Sample documents in agentic_rag.{collection_name}:")

for doc in collection.find().limit(3):
    print("\n--- Document ---")
    print("📄 page_content:", doc.get("page_content"))
    print("🧠 embedding present:", "embedding" in doc)
    print("📎 metadata:", doc.get("metadata"))
