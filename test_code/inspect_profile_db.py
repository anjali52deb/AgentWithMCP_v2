from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_ATLAS_URI"))

collection = client["agentic_rag"]["Profile_DB"]

print("\n📂 Sample documents in agentic_rag.Profile_DB:")
for doc in collection.find().limit(3):
    print("\n--- Document ---")
    print("📄 page_content:", doc.get("page_content"))
    print("🧠 embedding present:", "embedding" in doc)
    print("📎 metadata:", doc.get("metadata"))
