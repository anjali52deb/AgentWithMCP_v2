# mongo_utils.py

import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
CONFIG_PATH = os.getenv("MONGO_CONFIG_PATH", "mongo_config.json")


# def load_mongo_config():
#     with open(CONFIG_PATH, "r") as f:
#         return json.load(f)
def load_mongo_config():
    config_path = os.getenv("MONGO_CONFIG_PATH", "mongo_config.json")
    with open(config_path, "r") as f:
        return json.load(f)


def connect_to_mongo(collection_name: str):
    client = MongoClient(MONGO_URI)
    db = client["agentic_rag_vectors"]  # ✅ hardcoded default DB
    return db[collection_name]
