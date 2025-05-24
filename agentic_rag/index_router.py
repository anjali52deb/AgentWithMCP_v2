# index_router.py

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")

def route_index(tag: str):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config.get(tag, config.get("default"))


# # index_router.py

# """
# Routes document classification tags to specific Pinecone index names.
# Includes fallback normalization and default routing.
# """

# def get_index_for_tag(tag: str) -> str:
#     tag = tag.lower().strip()

#     # Optional normalization
#     if "hr" in tag or "human" in tag:
#         tag = "human resources"
#     elif "finance" in tag:
#         tag = "finance"
#     elif "policy" in tag:
#         tag = "compliance"

#     tag_to_index = {
#         "human resources": "agentic-rag-dense",
#         "compliance": "agentic-rag-dense",
#         "finance": "agentic-rag-dense",
#         "security": "agentic-rag-dense",
#         "operations": "agentic-rag-dense",
#         # Add more as needed
#     }

#     if tag in tag_to_index:
#         return tag_to_index[tag]
#     else:
#         raise ValueError(f"❌ No matching index found for tag: {tag}")
