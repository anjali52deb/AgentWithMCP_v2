# store_pipeline.py

import os
import sys
from uuid import uuid4
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agentic_rag.LLM_LangChain import split_text_into_chunks
from agentic_rag.attachment_handlers import extract_text_from_file
from agentic_rag.mongo_client import get_mongo_vectorstore
from agentic_rag.index_router import route_index
from agentic_rag.store_logger import log_store_event
from agentic_rag.utils import get_file_hash

from langchain.docstore.document import Document

load_dotenv()

def generate_doc_objects(text_chunks, metadata=None):
    return [
        Document(page_content=chunk, metadata=metadata or {})
        for chunk in text_chunks
    ]

def store_to_mongodb(file_path: str, tag: str = "default"):
    print(f"📥 Starting STORE for file: {file_path} | tag: {tag}")

    config = route_index(tag)
    db_name = config.get("db_name")
    collection_name = config.get("collection_name")
    index_name = config.get("index_name")

    extracted_text = extract_text_from_file(file_path)
    if not extracted_text:
        print("❌ No text extracted from file. Aborting.")
        return

    text_chunks = split_text_into_chunks(extracted_text)
    print(f"[DEBUG] 📄 Extracted into {len(text_chunks)} chunks")

    metadata = {"source": os.path.basename(file_path)}
    documents = generate_doc_objects(text_chunks, metadata=metadata)

    vectorstore = get_mongo_vectorstore(
        index_name=index_name,
        db_name=db_name,
        collection_name=collection_name
    )

    print(f"[DEBUG] 📦 Storing {len(documents)} docs to MongoDB Atlas ({db_name}.{collection_name})")

    # ✅ This is the correct, safe way:
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    doc_ids = [str(uuid4()) for _ in documents]

    vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=doc_ids)

    file_hash = get_file_hash(file_path)
    log_store_event(
        file_name=os.path.basename(file_path),
        chunk_count=len(documents),
        status="success",
        file_hash=file_hash
    )

    print("✅ STORE flow completed successfully!")


