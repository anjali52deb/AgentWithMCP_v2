# retriever_factory.py

from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from pymongo import MongoClient
from dotenv import load_dotenv
import os, json

# Load env variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Load mongo_config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "mongo_config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)


def get_retriever_model(subject: str, provider: str):
    provider = provider.lower()
    subject_config = CONFIG.get(subject, CONFIG.get("default"))

    db_name = subject_config["db_name"]
    index_name = subject_config["index_name"]
    collection_name = subject_config["collection_name"]

    print(f"[DEBUG] Building retriever for subject={subject}, index={index_name}, provider={provider}")


    client = MongoClient(MONGO_URI)
    collection = client[db_name][collection_name]

    # Select embedding provider
    if provider == "gpt":
        embedding_model = OpenAIEmbeddings()
    elif provider == "gemini":
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    # Build vector retriever
    # vectorstore = MongoDBAtlasVectorSearch(
    #     collection=collection,
    #     embedding=embedding_model,
    #     index_name=index_name
    # )

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embedding_model,
        index_name=index_name,
        text_key="chunk_text"  # ✅ Needed for matching
)


    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
