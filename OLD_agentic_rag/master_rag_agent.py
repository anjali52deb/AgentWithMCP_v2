# master_rag_agent.py

import os
from agentic_rag.store_pipeline import store_to_mongodb
from agentic_rag.retrieve_pipeline import retrieve_from_mongodb

from agentic_rag.log_metadata_reader import file_hash_already_stored
from agentic_rag.utils import get_file_hash
from agentic_rag.store_logger import log_store_event

def route_mode(mode: str, input_value: str, tag: str = None):
    if mode == "store":
        file_name = os.path.basename(input_value)
        file_hash = get_file_hash(input_value)

        if file_hash_already_stored(file_hash):
            print(f"⚠️  SKIPPED: File '{file_name}' (hash exists) already stored.")
            return f"⛔ STORE skipped — duplicate content: {file_name}"

        print(f"\n🚀 RAG-STORE Triggered → file: {file_name}")
        store_to_mongodb(input_value, tag=tag)

        # # Optional: log file_hash if not already in store_pipeline
        # log_store_event(
        #     file_name=file_name,
        #     chunk_count=0,  # actual count is already logged inside store_pipeline
        #     status="logged",
        #     file_hash=file_hash
        # )

        return f"✅ STORE completed: {file_name}"

    elif mode == "retrieve":
        print(f"\n🧠 RAG-RETRIEVE Triggered → query: {input_value}")
        answer = retrieve_from_mongodb(input_value, tag=tag)
        return answer

    else:
        raise ValueError(f"❌ Invalid mode: '{mode}'. Use 'store' or 'retrieve'.")


# # master_rag_agent.py

# import os
# from agentic_rag.store_pipeline import store_to_mongodb
# from agentic_rag.retrieve_pipeline import retrieve_from_mongodb
# from agentic_rag.log_metadata_reader import file_already_stored

# def route_mode(mode: str, input_value: str, tag: str = None):
#     """
#     RAG router to select between store or retrieve.
#     - mode: "store" or "retrieve"
#     - input_value: file path (for store) or user query (for retrieve)
#     - tag: Optional tag for retrieval index config
#     """
#     if mode == "store":
#         file_name = os.path.basename(input_value)

#         if file_already_stored(file_name):
#             print(f"⚠️  SKIPPED: File '{file_name}' already stored in MongoDB log.")
#             return f"⛔ STORE skipped — already exists: {file_name}"

#         print(f"\n🚀 RAG-STORE Triggered → file: {file_name}")
#         store_to_mongodb(input_value)
#         return f"✅ STORE completed: {file_name}"

#     elif mode == "retrieve":
#         print(f"\n🧠 RAG-RETRIEVE Triggered → query: {input_value}")
#         answer = retrieve_from_mongodb(input_value, tag=tag)
#         return answer

#     else:
#         raise ValueError(f"❌ Invalid mode: '{mode}'. Use 'store' or 'retrieve'.")
