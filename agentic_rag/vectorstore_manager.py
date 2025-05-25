# vectorstore_manager.py

from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
import os

def get_vectorstore_instance(db_name: str) -> MongoDBAtlasVectorSearch:
    connection_string = os.getenv("MONGODB_ATLAS_URI")
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    return MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=connection_string,
        namespace=f"rag_agent.{db_name}",  # or just db_name depending on setup
        embedding=embedding_model
    )
