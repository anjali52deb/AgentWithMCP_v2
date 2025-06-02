# Required: pip install pandas beautifulsoup4 openpyxl python-dotenv

"""
Agentic-RAG STORE Pipeline (Improved)
- Fully structured block-wise based on architecture
- Includes print-based debugging for every key step
- Production-ready + human-readable for tracing
"""

import os
import hashlib
import time
from pathlib import Path
import json
import traceback
import logging
from pymongo import MongoClient

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# ============================
# 🔐 Load environment
# ============================
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("❌ OPENAI_API_KEY not set in .env")

# ============================
# 🪵 Logging setup
# ============================
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_to_file = os.getenv("LOG_TO_FILE", "false").lower() == "true"
log_config = {
    "level": getattr(logging, log_level, logging.INFO),
    "format": "%(asctime)s - %(levelname)s - %(message)s"
}
if log_to_file:
    os.makedirs("logs", exist_ok=True)
    log_config["filename"] = "test_code/store_log.txt"
    log_config["filemode"] = "a"
logging.basicConfig(**log_config)


# ============================
# 🔌 MongoDB Client
# ============================
def get_mongo_client():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise EnvironmentError("❌ MONGODB_URI not set in .env")
    return MongoClient(uri)


# ============================================
# 🧩 Step 1: Input Handling
# ============================================

def load_config(config_path=None):
    if config_path is None:
        base = os.path.dirname(__file__)
        config_path = os.path.join(base, "mongo_config.json")
    print("🔧 Loading configuration from:", config_path)
    return json.load(open(config_path))



def extract_file_metadata(file_path: str, user_id: str) -> dict:
    print(f"📁 Extracting metadata for: {file_path}")
    file = Path(file_path)
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return {
        "file_name": file.name,
        "file_path": file_path,
        "file_size": file.stat().st_size,
        "user_id": user_id,
        "upload_time": time.time(),
        "file_hash": file_hash
    }


# ============================================
# 🗂️ Step 2: Log Metadata Check
# ============================================
def is_duplicate_upload(log_config, metadata) -> bool:
    client = get_mongo_client()
    logs_collection = client[log_config['db_name']][log_config['store_logs']]
    result = logs_collection.find_one({"file_hash": metadata["file_hash"]})
    if result:
        print("⚠️ Duplicate file detected in logs.")
    return result is not None


# ============================================
# 🧠 Step 2.5: Subject Detection from Filename
# ============================================
def detect_subject_from_filename(file_name: str, routing_keywords: dict) -> (str, str):
    print(f"🔍 Detecting subject for file: {file_name}")
    name_lower = file_name.lower()
    for subject, prefixes in routing_keywords.items():
        for prefix in prefixes:
            if name_lower.startswith(prefix):
                print(f"✅ Subject matched via tag: {subject}")
                return subject, "tag"
    print("❓ No subject match found. Using default.")
    return "default", "default"


# ============================================
# ✂️ Step 3: Chunking and Preprocessing
# ============================================
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    print(f"🔪 Chunking text with size={chunk_size}, overlap={overlap}")
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += chunk_size - overlap
    print(f"🧩 Total chunks created: {len(chunks)}")
    return chunks


# ============================================
# 🧠 Step 4: Embedding (No Classification)
# ============================================
# def embed_chunks(chunks: list, embedding_fn, subject: str, metadata=None) -> list:
#     print("🧠 Embedding chunks...")
#     results = []
#     for idx, chunk in enumerate(chunks):
#         try:
#             embedding = embedding_fn(chunk)
#             results.append({
#                 "chunk_text": chunk,
#                 "embedding": embedding,
#                 "subject": subject,
#                 "source_file": metadata.get("file_name"),
#                 "file_hash": metadata.get("file_hash"),
#                 "user_id": metadata.get("user_id"),
#                 "upload_time": metadata.get("upload_time"),
#                 "chunk_index": idx,
#                 "total_chunks": len(chunks)
#             })
#         except Exception as e:
#             print(f"❌ Embedding failed for chunk {idx}: {e}")
#             logging.error(f"❌ Failed embedding for chunk {idx}: {e}", exc_info=True)
#     print(f"✅ Embedded chunks: {len(results)}")
#     return results

def embed_chunks(chunks: list, embedding_fn, subject: str, metadata=None) -> list:
    print("🧠 Embedding chunks...")
    results = []

    for idx, chunk in enumerate(chunks):
        try:
            # ✅ Step: Generate hash per chunk
            chunk_hash = hashlib.md5(chunk.encode("utf-8")).hexdigest()

            # ✅ Step: Embed and structure result
            embedding = embedding_fn(chunk)
            results.append({
                "chunk_text": chunk,
                "embedding": embedding,
                "subject": subject,
                "source_file": metadata.get("file_name"),
                "file_hash": metadata.get("file_hash"),
                "user_id": metadata.get("user_id"),
                "upload_time": metadata.get("upload_time"),
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "metadata": {
                    "chunk_hash": chunk_hash
                }
            })

            print(f"🔢 Chunk {idx+1}/{len(chunks)} | hash: {chunk_hash[:8]}... stored ✅")

        except Exception as e:
            print(f"❌ Embedding failed for chunk {idx}: {e}")
            logging.error(f"❌ Failed embedding for chunk {idx}: {e}", exc_info=True)

    print(f"✅ Embedded chunks: {len(results)}")
    return results


# ============================================
# 💾 Step 5: Store Vector Info to DB
# ============================================
def store_vectors_to_db(embedded_chunks: list, config: dict, subject: str):
    print(f"📦 Storing chunks to DB for subject: {subject}")
    db_config = config.get(subject, config["default"])
    client = get_mongo_client()
    collection = client[db_config['db_name']][db_config['collection_name']]
    collection.insert_many(embedded_chunks)
    logging.info(f"✅ Stored {len(embedded_chunks)} chunks to DB: {db_config['collection_name']}")


# ============================================
# 📝 Step 6: Write Log Metadata
# ============================================
def log_store_metadata(log_config: dict, metadata: dict, subject: str, status: str, chunk_count: int, chunk_size: int, chunk_overlap: int, subject_source: str):
    print(f"📝 Logging store metadata for file: {metadata['file_name']}")
    client = get_mongo_client()
    log_coll = client[log_config['db_name']][log_config['store_logs']]
    log_entry = metadata.copy()
    log_entry.update({
        "subject": subject,
        "status": status,
        "chunk_count": chunk_count,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "embedding_model": "OpenAIEmbeddings",
        "classifier_model": "None",
        "store_intent_source": subject_source
    })
    log_coll.insert_one(log_entry)
    logging.info("📄 Log written with full traceability.")


# ============================================
# 📄 File Loader Utility (multi-format)
# ============================================
import hashlib  # if not already imported

def generate_chunk_hash(chunk_text: str) -> str:
    """Generate a consistent hash for a text chunk."""
    return hashlib.md5(chunk_text.encode("utf-8")).hexdigest()


def extract_text_from_file(file_path: str) -> str:
    print(f"📄 Extracting text from file: {file_path}")
    try:
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            text = "\n".join(doc.page_content for doc in documents)
        elif file_path.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            text = "\n".join(doc.page_content for doc in documents)
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path)
            documents = loader.load()
            text = "\n".join(doc.page_content for doc in documents)
        elif file_path.endswith(".csv"):
            import pandas as pd
            df = pd.read_csv(file_path)
            text = df.to_string(index=False)
        elif file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            text = json.dumps(data, indent=2)
        elif file_path.endswith(".xlsx"):
            import pandas as pd
            df = pd.read_excel(file_path, sheet_name=None)
            text = "\n\n".join(f"{sheet}\n{df[sheet].to_string(index=False)}" for sheet in df)
        elif file_path.endswith(".html"):
            from bs4 import BeautifulSoup
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            text = soup.get_text(separator="\n")
        elif file_path.endswith(".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            raise ValueError("Unsupported file type.")

        print(f"📏 Extracted {len(text)} characters from file.")
        return text

    except Exception as e:
        print(f"❌ Failed to extract text: {e}")
        logging.error(f"❌ Failed to extract text: {e}", exc_info=True)
        return ""


# ============================================
# 🚀 Main STORE Pipeline
# ============================================
def store_pipeline(file_path: str, user_id: str, config_path="mongo_config.json"):
    try:
        config = load_config(config_path)
        log_config = config["logs"]
        routing_keywords = config.get("routing_keywords", {})
        default_chunk_size = config.get("chunk_size", 500)
        default_chunk_overlap = config.get("chunk_overlap", 100)

        metadata = extract_file_metadata(file_path, user_id)
        print("🔄 Running pipeline for:", metadata["file_name"])

        if is_duplicate_upload(log_config, metadata):
            print("⚠️ Skipped duplicate upload.")
            return

        subject, subject_source = detect_subject_from_filename(metadata["file_name"], routing_keywords)
        subject_config = config.get(subject, config["default"])
        chunk_size = subject_config.get("chunk_size", default_chunk_size)
        chunk_overlap = subject_config.get("chunk_overlap", default_chunk_overlap)

        text = extract_text_from_file(file_path)
        if not text.strip():
            print("❌ Empty or unreadable content. Skipping.")
            return

        chunks = chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
        if not chunks:
            print("❌ No chunks created. Aborting.")
            return

        embedding_model = OpenAIEmbeddings()
        embedded = embed_chunks(
            chunks,
            embedding_fn=embedding_model.embed_query,
            subject=subject,
            metadata=metadata
        )

        if not embedded:
            print("❌ No embeddings generated. Aborting.")
            return

        store_vectors_to_db(embedded, config, subject)

        log_store_metadata(
            log_config,
            metadata,
            subject,
            status="completed",
            chunk_count=len(embedded),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            subject_source=subject_source
        )

        print("✅ Pipeline complete for:", metadata["file_name"])

    except Exception as e:
        print("💥 Exception occurred in pipeline:", e)
        logging.error("💥 Pipeline failed", exc_info=True)


# ============================================
# 📂 Multi-file Batch Runner
# ============================================
def store_multiple_files(file_paths: list, user_id: str, config_path="mongo_config.json"):
    for path in file_paths:
        print(f"🔁 Processing: {path}")
        try:
            store_pipeline(file_path=path, user_id=user_id, config_path=config_path)
        except Exception as e:
            print(f"💥 Error while processing {path}: {e}")
            logging.error(f"💥 Failed on {path}", exc_info=True)