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




# =======================================================
# from langchain_community.vectorstores import MongoDBAtlasVectorSearch
# from langchain_openai import OpenAIEmbeddings
# import os

# def get_vectorstore_instance(db_name: str) -> MongoDBAtlasVectorSearch:
#     connection_string = os.getenv("MONGODB_ATLAS_URI")
#     embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

#     return MongoDBAtlasVectorSearch.from_connection_string(
#         connection_string=connection_string,
#         namespace=f"rag_agent.{db_name}",  # or just db_name depending on setup
#         embedding=embedding_model
#     )
