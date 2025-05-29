# index_manager.py

import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Load secrets
MONGODB_ATLAS_PUBLIC_KEY = os.getenv("MONGODB_ATLAS_PUBLIC_KEY")
MONGODB_ATLAS_PRIVATE_KEY = os.getenv("MONGODB_ATLAS_PRIVATE_KEY")
MONGODB_ATLAS_PROJECT_ID = os.getenv("MONGODB_ATLAS_PROJECT_ID")
MONGODB_ATLAS_CLUSTER = os.getenv("MONGODB_ATLAS_CLUSTER_NAME")

# API Endpoint
API_URL = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{MONGODB_ATLAS_PROJECT_ID}/clusters/{MONGODB_ATLAS_CLUSTER}/fts/indexes"

# Template for vector index
def get_vector_index_payload(db_name, collection_name, embedding_field="embedding"):
    return {
        "collectionName": collection_name,
        "database": "rag_agent",
        "name": f"{collection_name}_vector_index",
        "mappings": {
            "dynamic": False,
            "fields": [
                {
                    "type": "vector",
                    "path": embedding_field,
                    "numDimensions": 1536,  # adjust as per embedding model
                    "similarity": "cosine"
                }
            ]
        }
    }

def create_vector_index(db_name, collection_name):
    payload = get_vector_index_payload(db_name, collection_name)
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        API_URL,
        auth=(MONGODB_ATLAS_PUBLIC_KEY, MONGODB_ATLAS_PRIVATE_KEY),
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code == 201:
        print(f"✅ Index created for {db_name}.{collection_name}")
    elif response.status_code == 409:
        print(f"⚠️ Index already exists for {db_name}.{collection_name}")
    else:
        print(f"❌ Failed to create index: {response.status_code}")
        print(response.text)

# Example usage
if __name__ == "__main__":
    # Change these as needed
    db_name = "rag_agent"
    # collection_list = ["Profile_DB", "History_DB", "Misc_DB"]
    collection_list = ["test"]


    for collection in collection_list:
        create_vector_index(db_name, collection)
