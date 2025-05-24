# store_pipeline.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from uuid import uuid4


from agentic_rag.LLM_LangChain import split_text_into_chunks
from agentic_rag.attachment_handlers import extract_text_from_file
from agentic_rag.store_logger import log_store_event
from agentic_rag.mongo_client import get_mongo_vectorstore
from agentic_rag.utils import get_file_hash

from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document

load_dotenv()  # Load OpenAI key and Mongo URI from .env

def generate_doc_objects(text_chunks, metadata=None):
    return [
        Document(page_content=chunk, metadata=metadata or {})
        for chunk in text_chunks
    ]

def store_to_mongodb(file_path: str):
    print(f"📥 Starting STORE for file: {file_path}")

    extracted_text = extract_text_from_file(file_path)
    if not extracted_text:
        print("❌ No text extracted from file. Aborting.")
        return

    text_chunks = split_text_into_chunks(extracted_text)
    print(f"[DEBUG] 📄 Extracted into {len(text_chunks)} chunks")

    metadata = {"source": os.path.basename(file_path)}
    documents = generate_doc_objects(text_chunks, metadata=metadata)

    vectorstore = get_mongo_vectorstore()
    print(f"[DEBUG] 📦 Storing {len(documents)} docs to MongoDB Atlas")

    for i, doc in enumerate(documents):
        print(f"\n📄 Chunk {i+1}:\n{doc.page_content[:300]}")

    doc_ids = [str(uuid4()) for _ in documents]
    vectorstore.add_documents(documents=documents, ids=doc_ids)

    # ✅ Log the event
    # log_store_event(
    #     file_name=os.path.basename(file_path),
    #     chunk_count=len(documents),
    #     status="success"
    # )

    file_hash = get_file_hash(file_path)

    log_store_event(
        file_name=os.path.basename(file_path),
        chunk_count=len(documents),
        status="success",
        file_hash=file_hash
    )

    print("✅ STORE flow completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python store_pipeline.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    store_to_mongodb(file_path)
