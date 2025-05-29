# mongo_client.py

import os
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from agentic_rag.config import MONGO_URI, VECTOR_DB_NAME, VECTOR_COLLECTION

def get_mongo_client():
    mongo_uri = os.getenv("MONGODB_ATLAS_URI")
    return MongoClient(mongo_uri)


def get_mongo_vectorstore(index_name="default", db_name=None, collection_name=None):
    client = MongoClient(MONGO_URI)

    db = client[db_name or VECTOR_DB_NAME]
    collection = db[collection_name or VECTOR_COLLECTION]

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=index_name
    )




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
