# index_router.py

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")

def route_index(tag: str):
    """
    Returns full routing config for a given tag.
    Includes db_name, collection_name, index_name, top_k, and llm.
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config.get(tag, config.get("default"))




# # index_router.py

# import json
# import os

# CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")

# def route_index(tag: str):
#     with open(CONFIG_PATH, "r", encoding="utf-8") as f:
#         config = json.load(f)

#     return config.get(tag, config.get("default"))

