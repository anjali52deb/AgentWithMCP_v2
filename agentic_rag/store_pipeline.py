# # store_pipeline.py
import os
import hashlib
from uuid import uuid4
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.docstore.document import Document

from agentic_rag.utils import load_and_split_file, guess_subject_tag
from agentic_rag.mongo_client import get_mongo_vectorstore, log_event, get_mongo_client

def compute_md5(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def store_to_mongodb(file_path, tag=None):
    file_name = os.path.basename(file_path)
    file_hash = compute_md5(file_path)
    subject_tag = tag  # NEW: compatible with old logic
    print(f"\n📥 Starting STORE for file: {file_path} | tag: {subject_tag or 'auto'}")

    # Detect subject if not given
    if subject_tag is None:
        subject_tag = guess_subject_tag(file_name)

    db_name = "agentic_rag"
    collection_name = subject_tag
    index_name = f"vector_index_{subject_tag.lower()}"

    # Deduplication check
    mongo = get_mongo_client()
    collection = mongo[db_name][collection_name]
    if collection.find_one({"metadata.file_hash": file_hash}):
        print(f"⚠️ File already stored (hash match): {file_name}. Skipping.")
        return

    # Load & chunk
    text_chunks = load_and_split_file(file_path)
    print(f"[DEBUG] 📄 Extracted into {len(text_chunks)} chunks")

    documents = []
    for chunk in text_chunks:
        if isinstance(chunk, Document):
            text = chunk.page_content
        elif isinstance(chunk, str):
            text = chunk
        else:
            print(f"❌ Skipping unknown type: {type(chunk)} → {chunk}")
            continue

        metadata = {
            "source": file_name,
            "text": text,
            "file_hash": file_hash,
        }
        documents.append(Document(page_content=text, metadata=metadata))


    if not documents:
        print("⚠️ No valid text chunks found. Skipping.")
        return

    # Vectorstore
    vectorstore = get_mongo_vectorstore(
        db_name=db_name,
        collection_name=collection_name,
        index_name=index_name
    )
    print(f"✅ Collection '{collection_name}' already exists.")

    # Store
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    ids = [str(uuid4()) for _ in documents]
    vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    print(f"[DEBUG] 📦 Stored {len(documents)} docs to MongoDB Atlas ({db_name}.{collection_name})")

    # Preview
    print("\n[DEBUG] 🧾 Sample Document Preview:")
    print(f"📄 page_content = {documents[0].page_content[:500]}")
    print(f"📎 metadata = {documents[0].metadata}")

    # Log
    log_event({
        "type": "store",
        "file": file_name,
        "chunks": len(documents),
        "subject": subject_tag,
    })
    print(f"📝 Logged STORE event for: {file_name}")
    print("✅ STORE flow completed successfully!")

def store_multiple_files(file_paths, tag=None):
    for path in file_paths:
        try:
            store_to_mongodb(path, tag=tag)
        except Exception as e:
            print(f"❌ Failed to store {path}: {e}")

