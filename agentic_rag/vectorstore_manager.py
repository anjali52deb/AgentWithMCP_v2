# vectorstore_manager.py

from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_mongo_vectorstore(db_name, collection_name, index_name, embedding_model_name="text-embedding-3-small"):
    mongo_uri = os.getenv("MONGODB_ATLAS_URI")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    embedding_model = OpenAIEmbeddings(model=embedding_model_name)

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embedding_model,
        index_name=index_name,
        text_key="text"  # ✅ Important: We store vectors in 'text', not 'page_content'
    )

    return vectorstore

def get_vectorstore_instance(db_tuple):
    if not isinstance(db_tuple, tuple) or len(db_tuple) != 2:
        raise ValueError(f"Expected tuple (db_name, collection_name), got: {db_tuple}")

    db_name, collection_name = db_tuple
    index_name = f"vector_index_{collection_name.lower()}"
    embedding_model_name = "text-embedding-3-small"

    return get_mongo_vectorstore(
        db_name=db_name,
        collection_name=collection_name,
        index_name=index_name,
        embedding_model_name=embedding_model_name
    )
