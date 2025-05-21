# index_router.py

"""
Maps classification tags to vector DB indexes using config JSON
"""

import json
import os

# Load config once
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")

with open(CONFIG_PATH, "r") as f:
    DB_CONFIG = json.load(f)


def get_index_for_tag(tag: str) -> str:
    tag = tag.lower()
    for index, meta in DB_CONFIG.items():
        for keyword in meta.get("domain_tags", []):
            if keyword in tag:
                return index

    raise ValueError(f"❌ No matching index found for tag: {tag}")
