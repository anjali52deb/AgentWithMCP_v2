# mongo_client.py

# mongo_client.py

from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGODB_ATLAS_URI")
client = MongoClient(MONGO_URI)

def get_mongo_client():
    return client

def get_mongo_vectorstore(db_name, collection_name, index_name, embedding_model_name="text-embedding-3-small"):
    from langchain_community.vectorstores import MongoDBAtlasVectorSearch
    from langchain_community.embeddings import OpenAIEmbeddings

    return MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=MONGO_URI,
        namespace=f"{db_name}.{collection_name}",
        embedding=OpenAIEmbeddings(model=embedding_model_name),
        index_name=index_name
    )

def log_event(event_dict: dict):
    log_db = client["agentic_rag"]
    logs_collection = log_db["logs"]
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    logs_collection.insert_one(event_dict)









# ================
# import os
# from pymongo import MongoClient
# from langchain_mongodb import MongoDBAtlasVectorSearch
# from langchain_openai import OpenAIEmbeddings
# from agentic_rag.config import MONGO_URI, VECTOR_DB_NAME, VECTOR_COLLECTION

# def get_mongo_client():
#     mongo_uri = os.getenv("MONGODB_ATLAS_URI")
#     return MongoClient(mongo_uri)


# def get_mongo_vectorstore(index_name="default", db_name=None, collection_name=None):
#     client = MongoClient(MONGO_URI)

#     db = client[db_name or VECTOR_DB_NAME]
#     collection = db[collection_name or VECTOR_COLLECTION]

#     embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

#     return MongoDBAtlasVectorSearch(
#         collection=collection,
#         embedding=embeddings,
#         index_name=index_name
#     )




# # mongo_client.py

# from pymongo import MongoClient
# # from langchain_community.vectorstores import MongoDBAtlasVectorSearch
# from langchain_mongodb import MongoDBAtlasVectorSearch
# from langchain_openai import OpenAIEmbeddings

# from agentic_rag.config import MONGO_URI, VECTOR_DB_NAME, VECTOR_COLLECTION

# def get_mongo_vectorstore(index_name="default"):
#     client = MongoClient(MONGO_URI)
#     collection = client[VECTOR_DB_NAME][VECTOR_COLLECTION]

#     embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

#     return MongoDBAtlasVectorSearch(
#         collection=collection,
#         embedding=embeddings,
#         index_name=index_name  # ✅ now dynamic
#     )
