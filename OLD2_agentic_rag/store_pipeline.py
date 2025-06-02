# # # # # # store_pipeline.py
import os
import hashlib
import json
from pymongo import MongoClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from agentic_rag.file_loader import load_file
from agentic_rag.vectorstore_manager import get_mongo_vectorstore
from agentic_rag.logger import log_store_event
from agentic_rag.config import MONGO_URI

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")
with open(CONFIG_PATH, "r") as f:
    VECTOR_DB_CONFIG = json.load(f)

def compute_md5(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def compute_chunk_hash(text: str) -> str:
    normalized = ' '.join(text.strip().lower().split())
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)

def classify_subject_from_filename(filename: str) -> str:
    name = filename.lower()
    if "finance" in name or "invoice" in name:
        return "history"
    elif "employee" in name or "profile" in name:
        return "profile"
    else:
        return "default"

def get_vector_config(subject_tag: str) -> dict:
    return VECTOR_DB_CONFIG.get(subject_tag.lower(), VECTOR_DB_CONFIG["default"])

def store_to_mongodb(file_path: str, tag: str = "auto"):
    file_name = os.path.basename(file_path)
    file_hash = compute_md5(file_path)
    print(f"\n📥 Starting STORE for file: {file_name} | tag: {tag}")

    subject_tag = tag if tag != "auto" else classify_subject_from_filename(file_name)
    vector_config = get_vector_config(subject_tag)

    db_name = vector_config["db_name"]
    collection_name = vector_config["collection_name"]
    index_name = vector_config.get("index_name", f"vector_index_{collection_name.lower()}")

    print(f"🔍 Subject: {subject_tag} → DB: {db_name}, Collection: {collection_name}, Index: {index_name}")

    documents = load_file(file_path)
    if not documents:
        print(f"⚠️ No content extracted from: {file_name}")
        return

    chunks = chunk_documents(documents)
    print(f"[DEBUG] 📄 Extracted into {len(chunks)} chunks")

    prepared_chunks = []
    for i, chunk in enumerate(chunks):
        text = chunk.page_content
        chunk_hash = compute_chunk_hash(text)
        print(f"🔎 Chunk {i+1}: hash = {chunk_hash}, file = {file_name}, text[:60] = {text[:60]!r}")
        chunk.metadata = {
            "source": file_name,
            "file_hash": file_hash,
            "chunk_hash": chunk_hash
        }
        prepared_chunks.append(Document(page_content=text, metadata=chunk.metadata))

    vectorstore = get_mongo_vectorstore(db_name, collection_name, index_name)
    raw_collection = MongoClient(MONGO_URI)[db_name][collection_name]
    try:
        raw_collection.create_index(
            [("metadata.chunk_hash", 1)],
            name="unique_chunk_hash",
            unique=True
        )
        print(f"🔐 Ensured unique index on metadata.chunk_hash for {db_name}.{collection_name}")
    except Exception as e:
        print(f"⚠️ Index creation failed: {e}")

    inserted = 0
    for i, doc in enumerate(prepared_chunks):
        try:
            vectorstore.add_documents([doc])
            print(f"✅ Inserted chunk {i+1}")
            inserted += 1
        except Exception as e:
            if "duplicate key" in str(e).lower():
                print(f"🟡 Duplicate chunk skipped: {doc.metadata['chunk_hash']}")
            else:
                print(f"❌ Error inserting chunk {i+1}: {e}")

    log_store_event(
        file_name=file_name,
        chunk_count=inserted,
        status="stored",
        file_hash=file_hash,
        additional_info={"subject": subject_tag}
    )
    print(f"✅ STORE completed for: {file_name} ({inserted} chunks inserted)")

def store_multiple_files(file_paths, tag=None):
    for path in file_paths:
        try:
            store_to_mongodb(path, tag=tag or "auto")
        except Exception as e:
            print(f"❌ Failed to store {path}: {e}")

# import os
# import hashlib
# import json
# from pymongo import MongoClient
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema import Document

# from agentic_rag.file_loader import load_file
# from agentic_rag.vectorstore_manager import get_mongo_vectorstore
# from agentic_rag.logger import log_store_event
# from agentic_rag.config import MONGO_URI

# # --- Load Vector DB Config JSON ---
# CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")
# with open(CONFIG_PATH, "r") as f:
#     VECTOR_DB_CONFIG = json.load(f)

# # --- Utility Functions ---
# def compute_md5(file_path):
#     with open(file_path, 'rb') as f:
#         return hashlib.md5(f.read()).hexdigest()

# def compute_chunk_hash(text: str) -> str:
#     return hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()

# def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
#     splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
#     return splitter.split_documents(documents)

# # --- Subject Classification ---
# def classify_subject_from_filename(filename: str) -> str:
#     name = filename.lower()
#     if "finance" in name or "invoice" in name:
#         return "history"
#     elif "employee" in name or "profile" in name:
#         return "profile"
#     else:
#         return "default"

# def get_vector_config(subject_tag: str) -> dict:
#     return VECTOR_DB_CONFIG.get(subject_tag.lower(), VECTOR_DB_CONFIG["default"])

# # --- Main STORE Logic ---
# def store_to_mongodb(file_path: str, tag: str = "auto"):
#     file_name = os.path.basename(file_path)
#     file_hash = compute_md5(file_path)
#     print(f"\n📥 Starting STORE for file: {file_name} | tag: {tag}")

#     subject_tag = tag if tag != "auto" else classify_subject_from_filename(file_name)
#     vector_config = get_vector_config(subject_tag)

#     db_name = vector_config["db_name"]
#     collection_name = vector_config["collection_name"]
#     index_name = vector_config.get("index_name", f"vector_index_{collection_name.lower()}")

#     print(f"🔍 Subject: {subject_tag} → DB: {db_name}, Collection: {collection_name}, Index: {index_name}")

#     documents = load_file(file_path)
#     if not documents:
#         print(f"⚠️ No content extracted from: {file_name}")
#         return

#     chunks = chunk_documents(documents)
#     print(f"[DEBUG] 📄 Extracted into {len(chunks)} chunks")

#     # Compute hashes and prepare documents
#     prepared_chunks = []
#     for chunk in chunks:
#         text = chunk.page_content
#         chunk_hash = compute_chunk_hash(text)
#         metadata = {
#             "source": file_name,
#             "file_hash": file_hash,
#             "chunk_hash": chunk_hash
#         }
#         prepared_chunks.append(Document(page_content=text, metadata=metadata))

#     print(f"🧪 Previewing {len(prepared_chunks)} prepared chunks:")
#     for i, doc in enumerate(prepared_chunks):
#         print(f"🔎 Chunk {i+1}: hash = {doc.metadata['chunk_hash']}, text[:60] = {doc.page_content[:60]!r}")

#     # Get vectorstore and enforce index
#     vectorstore = get_mongo_vectorstore(db_name, collection_name, index_name)
#     raw_collection = MongoClient(MONGO_URI)[db_name][collection_name]
#     try:
#         raw_collection.create_index(
#             [("metadata.chunk_hash", 1)],
#             name="unique_chunk_hash",
#             unique=True
#         )
#         print(f"🔐 Ensured unique index on metadata.chunk_hash for {db_name}.{collection_name}")
#     except Exception as e:
#         print(f"⚠️ Index creation failed: {e}")

#     inserted = 0
#     for i, doc in enumerate(prepared_chunks):
#         try:
#             vectorstore.add_documents([doc])
#             print(f"✅ Inserted chunk {i+1}")
#             inserted += 1
#         except Exception as e:
#             if "duplicate key" in str(e).lower():
#                 print(f"🟡 Duplicate chunk skipped: {doc.metadata['chunk_hash']}")
#             else:
#                 print(f"❌ Error inserting chunk {i+1}: {e}")

#     log_store_event(
#         file_name=file_name,
#         chunk_count=inserted,
#         status="stored",
#         file_hash=file_hash,
#         additional_info={"subject": subject_tag}
#     )
#     print(f"✅ STORE completed for: {file_name} ({inserted} chunks inserted)")

# def store_multiple_files(file_paths, tag=None):
#     for path in file_paths:
#         try:
#             store_to_mongodb(path, tag=tag or "auto")
#         except Exception as e:
#             print(f"❌ Failed to store {path}: {e}")


# # import os
# # import hashlib
# # import json
# # from pymongo import MongoClient
# # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # from langchain.schema import Document

# # from agentic_rag.file_loader import load_file
# # from agentic_rag.vectorstore_manager import get_mongo_vectorstore
# # from agentic_rag.logger import log_store_event
# # from agentic_rag.config import MONGO_URI

# # # --- Load Vector DB Config JSON ---
# # CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")
# # with open(CONFIG_PATH, "r") as f:
# #     VECTOR_DB_CONFIG = json.load(f)

# # # --- Utility Functions ---
# # def compute_md5(file_path):
# #     with open(file_path, 'rb') as f:
# #         return hashlib.md5(f.read()).hexdigest()

# # def compute_chunk_hash(text: str) -> str:
# #     return hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()

# # def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
# #     splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
# #     return splitter.split_documents(documents)

# # # --- Subject Classification ---
# # def classify_subject_from_filename(filename: str) -> str:
# #     name = filename.lower()
# #     if "finance" in name or "invoice" in name:
# #         return "history"
# #     elif "employee" in name or "profile" in name:
# #         return "profile"
# #     else:
# #         return "default"

# # def get_vector_config(subject_tag: str) -> dict:
# #     return VECTOR_DB_CONFIG.get(subject_tag.lower(), VECTOR_DB_CONFIG["default"])

# # # --- Main STORE Logic ---
# # def store_to_mongodb(file_path: str, tag: str = "auto"):
# #     file_name = os.path.basename(file_path)
# #     file_hash = compute_md5(file_path)
# #     print(f"\n📥 Starting STORE for file: {file_name} | tag: {tag}")

# #     subject_tag = tag if tag != "auto" else classify_subject_from_filename(file_name)
# #     vector_config = get_vector_config(subject_tag)

# #     db_name = vector_config["db_name"]
# #     collection_name = vector_config["collection_name"]
# #     index_name = vector_config.get("index_name", f"vector_index_{collection_name.lower()}")

# #     print(f"🔍 Subject: {subject_tag} → DB: {db_name}, Collection: {collection_name}, Index: {index_name}")

# #     documents = load_file(file_path)
# #     if not documents:
# #         print(f"⚠️ No content extracted from: {file_name}")
# #         return

# #     chunks = chunk_documents(documents)
# #     print(f"[DEBUG] 📄 Extracted into {len(chunks)} chunks")

# #     prepared_chunks = []
# #     for chunk in chunks:
# #         text = chunk.page_content
# #         chunk_hash = compute_chunk_hash(text)
# #         chunk.metadata = {
# #             "source": file_name,
# #             "file_hash": file_hash,
# #             "chunk_hash": chunk_hash,
# #             "text": text
# #         }
# #         prepared_chunks.append(Document(page_content=text, metadata=chunk.metadata))

# #     print(f"🧪 Previewing {len(prepared_chunks)} prepared chunks:")
# #     for i, chunk in enumerate(prepared_chunks):
# #         print(f"🔎 Chunk {i+1}: hash = {chunk.metadata['chunk_hash']}, text[:60] = {chunk.page_content[:60]!r}")

# #     # Initialize vectorstore and enforce deduplication via unique index
# #     vectorstore = get_mongo_vectorstore(db_name, collection_name, index_name)
# #     mongo_client = MongoClient(MONGO_URI)
# #     raw_collection = mongo_client[db_name][collection_name]
# #     try:
# #         raw_collection.create_index(
# #             [("metadata.chunk_hash", 1)],
# #             name="unique_chunk_hash",
# #             unique=True
# #         )
# #         print(f"🔐 Ensured unique index on metadata.chunk_hash for {db_name}.{collection_name}")
# #     except Exception as e:
# #         print(f"⚠️ Index creation failed: {e}")

# #     inserted = 0
# #     for i, chunk in enumerate(prepared_chunks):
# #         try:
# #             vectorstore.add_documents([chunk])
# #             print(f"✅ Inserted chunk {i+1}")
# #             inserted += 1
# #         except Exception as e:
# #             if "duplicate key" in str(e).lower():
# #                 print(f"🟡 Duplicate chunk skipped: {chunk.metadata['chunk_hash']}")
# #             else:
# #                 print(f"❌ Error inserting chunk {i+1}: {e}")

# #     log_store_event(
# #         file_name=file_name,
# #         chunk_count=inserted,
# #         status="stored",
# #         file_hash=file_hash,
# #         additional_info={"subject": subject_tag}
# #     )
# #     print(f"✅ STORE completed for: {file_name} ({inserted} chunks inserted)")

# # def store_multiple_files(file_paths, tag=None):
# #     for path in file_paths:
# #         try:
# #             store_to_mongodb(path, tag=tag or "auto")
# #         except Exception as e:
# #             print(f"❌ Failed to store {path}: {e}")
















# # # # # store_pipeline.py

# # # # import os
# # # # import hashlib
# # # # import json
# # # # from uuid import uuid4
# # # # from pymongo import MongoClient
# # # # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # # # from langchain.schema import Document

# # # # from agentic_rag.file_loader import load_file
# # # # from agentic_rag.vectorstore_manager import get_mongo_vectorstore
# # # # from agentic_rag.logger import log_store_event
# # # # from agentic_rag.config import MONGO_URI

# # # # # --- Load Vector DB Config JSON ---
# # # # CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")
# # # # with open(CONFIG_PATH, "r") as f:
# # # #     VECTOR_DB_CONFIG = json.load(f)

# # # # # --- Utility Functions ---
# # # # def compute_md5(file_path):
# # # #     with open(file_path, 'rb') as f:
# # # #         return hashlib.md5(f.read()).hexdigest()

# # # # # def compute_chunk_hash(text: str) -> str:
# # # # #     return hashlib.md5(text.encode('utf-8')).hexdigest()

# # # # def compute_chunk_hash(text: str) -> str:
# # # #     return hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()

# # # # def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
# # # #     splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
# # # #     return splitter.split_documents(documents)

# # # # # --- Subject Classification ---
# # # # def classify_subject_from_filename(filename: str) -> str:
# # # #     name = filename.lower()
# # # #     if "finance" in name or "invoice" in name:
# # # #         return "history"
# # # #     elif "employee" in name or "profile" in name:
# # # #         return "profile"
# # # #     else:
# # # #         return "default"

# # # # def get_vector_config(subject_tag: str) -> dict:
# # # #     return VECTOR_DB_CONFIG.get(subject_tag.lower(), VECTOR_DB_CONFIG["default"])

# # # # # --- Main STORE Logic ---
# # # # def store_to_mongodb(file_path: str, tag: str = "auto"):
# # # #     file_name = os.path.basename(file_path)
# # # #     file_hash = compute_md5(file_path)
# # # #     print(f"\n📥 Starting STORE for file: {file_name} | tag: {tag}")

# # # #     subject_tag = tag if tag != "auto" else classify_subject_from_filename(file_name)
# # # #     vector_config = get_vector_config(subject_tag)

# # # #     db_name = vector_config["db_name"]
# # # #     collection_name = vector_config["collection_name"]
# # # #     index_name = vector_config.get("index_name", f"vector_index_{collection_name.lower()}")

# # # #     print(f"🔍 Subject: {subject_tag} → DB: {db_name}, Collection: {collection_name}, Index: {index_name}")

# # # #     documents = load_file(file_path)
# # # #     if not documents:
# # # #         print(f"⚠️ No content extracted from: {file_name}")
# # # #         return

# # # #     chunks = chunk_documents(documents)
# # # #     print(f"[DEBUG] 📄 Extracted into {len(chunks)} chunks")

# # # #     prepared_chunks = []
# # # #     for chunk in chunks:
# # # #         text = chunk.page_content
# # # #         chunk_hash = compute_chunk_hash(text)
# # # #         chunk.metadata = {
# # # #             "source": file_name,
# # # #             "file_hash": file_hash,
# # # #             "chunk_hash": chunk_hash,
# # # #             "text": text
# # # #         }
# # # #         prepared_chunks.append(Document(page_content=text, metadata=chunk.metadata))

# # # #     print(f"🧪 Previewing {len(prepared_chunks)} prepared chunks:")
# # # #     for i, chunk in enumerate(prepared_chunks):
# # # #         print(f"🔎 Chunk {i+1}: hash = {chunk.metadata['chunk_hash']}, text[:60] = {chunk.page_content[:60]!r}")

# # # #     # Initialize vectorstore and enforce deduplication via unique index
# # # #     vectorstore = get_mongo_vectorstore(db_name, collection_name, index_name)

# # # #     mongo_client = MongoClient(MONGO_URI)
# # # #     raw_collection = mongo_client[db_name][collection_name]
# # # #     try:
# # # #         raw_collection.create_index(
# # # #             [("metadata.chunk_hash", 1)],
# # # #             name="unique_chunk_hash",
# # # #             unique=True
# # # #         )
# # # #         print(f"🔐 Ensured unique index on metadata.chunk_hash for {db_name}.{collection_name}")
# # # #     except Exception as e:
# # # #         print(f"⚠️ Index creation failed: {e}")

# # # #     inserted = 0
# # # #     for i, chunk in enumerate(prepared_chunks):
# # # #         try:
# # # #             vectorstore.add_documents([chunk])
# # # #             print(f"✅ Inserted chunk {i+1}")
# # # #             inserted += 1
# # # #         except Exception as e:
# # # #             if "duplicate key" in str(e).lower():
# # # #                 print(f"🟡 Duplicate chunk skipped: {chunk.metadata['chunk_hash']}")
# # # #             else:
# # # #                 print(f"❌ Error inserting chunk {i+1}: {e}")

# # # #     log_store_event(
# # # #         file_name=file_name,
# # # #         chunk_count=inserted,
# # # #         status="stored",
# # # #         file_hash=file_hash,
# # # #         additional_info={"subject": subject_tag}
# # # #     )
# # # #     print(f"✅ STORE completed for: {file_name} ({inserted} chunks inserted)")

# # # # def store_multiple_files(file_paths, tag=None):
# # # #     for path in file_paths:
# # # #         try:
# # # #             store_to_mongodb(path, tag=tag or "auto")
# # # #         except Exception as e:
# # # #             print(f"❌ Failed to store {path}: {e}")












# # # # # =================================================
# # # # # # store_pipeline.py

# # # # # import os
# # # # # import hashlib
# # # # # import json
# # # # # from uuid import uuid4
# # # # # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # # # # from langchain.schema import Document

# # # # # from agentic_rag.file_loader import load_file
# # # # # from agentic_rag.vectorstore_manager import get_mongo_vectorstore
# # # # # from agentic_rag.logger import log_store_event

# # # # # from pymongo import MongoClient
# # # # # from agentic_rag.config import MONGO_URI

# # # # # # --- Load Vector DB Config JSON ---

# # # # # CONFIG_PATH = os.path.join(os.path.dirname(__file__), "vector_db_config.json")
# # # # # with open(CONFIG_PATH, "r") as f:
# # # # #     VECTOR_DB_CONFIG = json.load(f)


# # # # # # --- Utility Functions ---

# # # # # def compute_md5(file_path):
# # # # #     with open(file_path, 'rb') as f:
# # # # #         return hashlib.md5(f.read()).hexdigest()

# # # # # def compute_chunk_hash(text: str) -> str:
# # # # #     return hashlib.md5(text.encode('utf-8')).hexdigest()

# # # # # def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
# # # # #     splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
# # # # #     return splitter.split_documents(documents)


# # # # # # --- Subject Classification & Config Resolution ---

# # # # # def classify_subject_from_filename(filename: str) -> str:
# # # # #     name = filename.lower()
# # # # #     if "finance" in name or "invoice" in name:
# # # # #         return "history"
# # # # #     elif "employee" in name or "profile" in name:
# # # # #         return "profile"
# # # # #     else:
# # # # #         return "default"

# # # # # def get_vector_config(subject_tag: str) -> dict:
# # # # #     key = subject_tag.lower()
# # # # #     return VECTOR_DB_CONFIG.get(key, VECTOR_DB_CONFIG["default"])


# # # # # # --- Main STORE Logic ---

# # # # # def store_to_mongodb(file_path: str, tag: str = "auto"):
# # # # #     file_name = os.path.basename(file_path)
# # # # #     file_hash = compute_md5(file_path)
# # # # #     print(f"\n📥 Starting STORE for file: {file_name} | tag: {tag}")

# # # # #     # Detect subject
# # # # #     subject_tag = tag if tag != "auto" else classify_subject_from_filename(file_name)
# # # # #     vector_config = get_vector_config(subject_tag)

# # # # #     db_name = vector_config["db_name"]
# # # # #     collection_name = vector_config["collection_name"]
# # # # #     index_name = vector_config.get("index_name", f"vector_index_{collection_name.lower()}")

# # # # #     print(f"🔍 Subject: {subject_tag} → DB: {db_name}, Collection: {collection_name}, Index: {index_name}")

# # # # #     # Load file
# # # # #     documents = load_file(file_path)
# # # # #     if not documents:
# # # # #         print(f"⚠️ No content extracted from: {file_name}")
# # # # #         return

# # # # #     # Chunk
# # # # #     chunks = chunk_documents(documents)
# # # # #     print(f"[DEBUG] 📄 Extracted into {len(chunks)} chunks")

# # # # #     # Prepare chunks
# # # # #     prepared_chunks = []
# # # # #     for chunk in chunks:
# # # # #         text = chunk.page_content
# # # # #         chunk_hash = compute_chunk_hash(text)
# # # # #         chunk.metadata = {
# # # # #             "source": file_name,
# # # # #             "file_hash": file_hash,
# # # # #             "chunk_hash": chunk_hash,
# # # # #             "text": text
# # # # #         }
# # # # #         prepared_chunks.append(Document(page_content=text, metadata=chunk.metadata))

# # # # #     print(f"🧪 Previewing {len(prepared_chunks)} prepared chunks:\n")
# # # # #     for i, chunk in enumerate(prepared_chunks):
# # # # #         print(f"🔎 Chunk {i+1}: hash = {chunk.metadata['chunk_hash']}")
# # # # #         print(f"    preview: {chunk.page_content[:100]}...\n")


# # # # #     # Init vectorstore
# # # # #     vectorstore = get_mongo_vectorstore(
# # # # #         db_name=db_name,
# # # # #         collection_name=collection_name,
# # # # #         index_name=index_name
# # # # #     )

# # # # #     # Auto-create unique index on metadata.chunk_hash
# # # # #     mongo_client = MongoClient(MONGO_URI)
# # # # #     raw_collection = mongo_client[db_name][collection_name]
# # # # #     try:
# # # # #         raw_collection.create_index(
# # # # #             [("metadata.chunk_hash", 1)],
# # # # #             name="unique_chunk_hash",
# # # # #             unique=True
# # # # #         )
# # # # #         print(f"🔐 Ensured unique index on metadata.chunk_hash for {db_name}.{collection_name}")
# # # # #     except Exception as e:
# # # # #         print(f"⚠️ Index creation failed: {e}")

# # # # #     # Store chunks — let MongoDB enforce dedup
# # # # #     try:
# # # # #         vectorstore.add_documents(prepared_chunks)
# # # # #         print(f"[DEBUG] 📦 Stored {len(prepared_chunks)} chunks to: {db_name}.{collection_name}")
# # # # #     except Exception as e:
# # # # #         if "duplicate key" in str(e).lower():
# # # # #             print("⚠️ Duplicate chunks skipped via unique index")
# # # # #         else:
# # # # #             raise

# # # # #     # Log
# # # # #     log_store_event(
# # # # #         file_name=file_name,
# # # # #         chunk_count=len(prepared_chunks),
# # # # #         status="stored",
# # # # #         file_hash=file_hash,
# # # # #         additional_info={"subject": subject_tag}
# # # # #     )
# # # # #     print(f"✅ STORE completed for: {file_name}")


# # # # # def store_multiple_files(file_paths, tag=None):
# # # # #     for path in file_paths:
# # # # #         try:
# # # # #             store_to_mongodb(path, tag=tag or "auto")
# # # # #         except Exception as e:
# # # # #             print(f"❌ Failed to store {path}: {e}")

# # # # # # import os
# # # # # # import hashlib
# # # # # # from uuid import uuid4
# # # # # # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # # # # # from langchain.schema import Document

# # # # # # from agentic_rag.file_loader import load_file
# # # # # # from agentic_rag.vectorstore_manager import get_vectorstore_instance, is_duplicate_file
# # # # # # from agentic_rag.logger import log_store_event


# # # # # # # --- Utility Functions ---

# # # # # # def compute_md5(file_path):
# # # # # #     """Compute MD5 hash of the full file (used for logging & deduplication)"""
# # # # # #     with open(file_path, 'rb') as f:
# # # # # #         return hashlib.md5(f.read()).hexdigest()

# # # # # # def compute_chunk_hash(text: str) -> str:
# # # # # #     """Compute hash for a text chunk"""
# # # # # #     return hashlib.md5(text.encode('utf-8')).hexdigest()

# # # # # # def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
# # # # # #     splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
# # # # # #     return splitter.split_documents(documents)


# # # # # # # --- Subject Classification & DB Mapping ---

# # # # # # def classify_subject_from_filename(filename: str) -> str:
# # # # # #     name = filename.lower()
# # # # # #     if "finance" in name or "invoice" in name:
# # # # # #         return "TransactionHistory"
# # # # # #     elif "employee" in name or "profile" in name:
# # # # # #         return "CompanyProfile"
# # # # # #     else:
# # # # # #         return "EverythingElse"

# # # # # # subject_to_db_map = {
# # # # # #     "CompanyProfile": ("Profile_DB", "profile_docs"),
# # # # # #     "TransactionHistory": ("History_DB", "history_docs"),
# # # # # #     "EverythingElse": ("Misc_DB", "misc_docs")
# # # # # # }


# # # # # # # --- Main STORE Logic ---

# # # # # # def store_to_mongodb(file_path: str, tag: str = "auto"):
# # # # # #     file_name = os.path.basename(file_path)
# # # # # #     file_hash = compute_md5(file_path)
# # # # # #     print(f"\n📥 Starting STORE for file: {file_name} | tag: {tag}")

# # # # # #     # Detect subject
# # # # # #     subject_tag = tag if tag != "auto" else classify_subject_from_filename(file_name)
# # # # # #     db_tuple = subject_to_db_map.get(subject_tag, subject_to_db_map["EverythingElse"])
# # # # # #     print(f"🔍 Subject guessed: {subject_tag} → DB: {db_tuple}")

# # # # # #     # Load file
# # # # # #     documents = load_file(file_path)
# # # # # #     if not documents:
# # # # # #         print(f"⚠️ No content extracted from: {file_name}")
# # # # # #         return

# # # # # #     # Chunk
# # # # # #     chunks = chunk_documents(documents)
# # # # # #     print(f"[DEBUG] 📄 Extracted into {len(chunks)} chunks")

# # # # # #     # Prepare chunks with metadata
# # # # # #     prepared_chunks = []
# # # # # #     for chunk in chunks:
# # # # # #         text = chunk.page_content
# # # # # #         chunk_hash = compute_chunk_hash(text)
# # # # # #         chunk.metadata = {
# # # # # #             "source": file_name,
# # # # # #             "file_hash": file_hash,
# # # # # #             "chunk_hash": chunk_hash,
# # # # # #             "text": text
# # # # # #         }
# # # # # #         prepared_chunks.append(Document(page_content=text, metadata=chunk.metadata))

# # # # # #     # Init vectorstore
# # # # # #     vectorstore = get_vectorstore_instance(db_tuple)

# # # # # #     # Dedup filter
# # # # # #     new_chunks = []
# # # # # #     for chunk in prepared_chunks:
# # # # # #         if is_duplicate_file(vectorstore, chunk.metadata["chunk_hash"]):
# # # # # #             print(f"🟡 Skipping duplicate chunk: {chunk.metadata['chunk_hash']}")
# # # # # #         else:
# # # # # #             new_chunks.append(chunk)

# # # # # #     if not new_chunks:
# # # # # #         print(f"⚠️ All chunks are duplicates. Skipping DB insert for {file_name}")
# # # # # #         return

# # # # # #     # Store to DB
# # # # # #     vectorstore.add_documents(new_chunks)
# # # # # #     print(f"[DEBUG] 📦 Stored {len(new_chunks)} chunks to: {db_tuple}")

# # # # # #     # Log
# # # # # #     log_store_event(
# # # # # #         file_name=file_name,
# # # # # #         chunk_count=len(new_chunks),
# # # # # #         status="stored",
# # # # # #         file_hash=file_hash,
# # # # # #         additional_info={"subject": subject_tag}
# # # # # #     )
# # # # # #     print(f"✅ STORE completed for: {file_name}")


# # # # # # def store_multiple_files(file_paths, tag=None):
# # # # # #     for path in file_paths:
# # # # # #         try:
# # # # # #             store_to_mongodb(path, tag=tag or "auto")
# # # # # #         except Exception as e:
# # # # # #             print(f"❌ Failed to store {path}: {e}")

# # # # # # ==============================================

# # # # # # import os
# # # # # # import hashlib
# # # # # # from uuid import uuid4
# # # # # # from langchain_community.embeddings import OpenAIEmbeddings
# # # # # # from langchain_community.vectorstores import MongoDBAtlasVectorSearch
# # # # # # from langchain.docstore.document import Document

# # # # # # from agentic_rag.utils import load_and_split_file, guess_subject_tag
# # # # # # from agentic_rag.mongo_client import get_mongo_vectorstore, log_event, get_mongo_client
# # # # # # from agentic_rag.config import get_vector_config
# # # # # # from agentic_rag.subject_db_mapper import get_db_and_collection_for_subject
# # # # # # from agentic_rag.logger import log_store_event

# # # # # # def compute_md5(file_path):
# # # # # #     with open(file_path, 'rb') as f:
# # # # # #         return hashlib.md5(f.read()).hexdigest()

# # # # # # def store_to_mongodb(file_path, tag=None):
# # # # # #     file_name = os.path.basename(file_path)
# # # # # #     file_hash = compute_md5(file_path)
    
# # # # # #     # subject_tag = tag  # NEW: compatible with old logic
# # # # # #     subject_tag = None if tag == "auto" else tag
# # # # # #     print(f"\n📥 Starting STORE for file: {file_path} | tag: {subject_tag or 'auto'}")

# # # # # #     # Detect subject if not given
# # # # # #     if subject_tag is None:
# # # # # #         subject_tag = guess_subject_tag(file_name)
# # # # # #         print(f"🔍 Subject guessed from filename: {subject_tag}")

# # # # # #     # Fetch config from JSON based on subject
# # # # # #     # vector_config = get_vector_config(subject_tag)

# # # # # #     # Normalize subject_tag before config lookup
# # # # # #     subject_key = subject_tag.lower()

# # # # # #     # Optional hard override mapping
# # # # # #     subject_key_map = {
# # # # # #         "companyprofile": "profile",
# # # # # #         "transactionhistory": "history",
# # # # # #         "misc": "misc"
# # # # # #     }
# # # # # #     subject_key = subject_key_map.get(subject_key, subject_key)
# # # # # #     vector_config = get_vector_config(subject_key)


# # # # # #     # Apply lowercase to subject_tag if index name is dynamic
# # # # # #     db_name = vector_config["db_name"]
# # # # # #     collection_name = vector_config["collection_name"]

# # # # # #     # Use hardcoded pattern with lowercase, OR override from config if present
# # # # # #     index_name = vector_config.get("index_name") or f"vector_index_{subject_tag.lower()}"

# # # # # #     # Optional safeguard:
# # # # # #     if "index_name" not in vector_config:
# # # # # #         print(f"⚠️ Using fallback index name: {index_name}")


# # # # # #     # Deduplication check
# # # # # #     mongo = get_mongo_client()
# # # # # #     collection = mongo[db_name][collection_name]
# # # # # #     # if collection.find_one({"metadata.file_hash": file_hash}):
# # # # # #     #     print(f"⚠️ File already stored (hash match): {file_name}. Skipping.")
# # # # # #     #     return

# # # # # #     # NEW: Cross-collection deduplication using store_logs
# # # # # #     log_db = mongo["agentic_rag_logs"]["store_logs"]
# # # # # #     if log_db.find_one({"metadata.file_hash": file_hash, "status": "stored"}):
# # # # # #         print(f"⚠️ File already stored (hash match): {file_name}. Skipping.")
# # # # # #         return



# # # # # #     # Load & chunk
# # # # # #     text_chunks = load_and_split_file(file_path)
# # # # # #     print(f"[DEBUG] 📄 Extracted into {len(text_chunks)} chunks")

# # # # # #     documents = []
# # # # # #     for chunk in text_chunks:
# # # # # #         if isinstance(chunk, Document):
# # # # # #             text = chunk.page_content
# # # # # #         elif isinstance(chunk, str):
# # # # # #             text = chunk
# # # # # #         else:
# # # # # #             print(f"❌ Skipping unknown type: {type(chunk)} → {chunk}")
# # # # # #             continue

# # # # # #         metadata = {
# # # # # #             "source": file_name,
# # # # # #             "text": text,
# # # # # #             "file_hash": file_hash,
# # # # # #         }
# # # # # #         documents.append(Document(page_content=text, metadata=metadata))


# # # # # #     if not documents:
# # # # # #         print("⚠️ No valid text chunks found. Skipping.")
# # # # # #         return

# # # # # #     # Vectorstore
# # # # # #     vectorstore = get_mongo_vectorstore(
# # # # # #         db_name=db_name,
# # # # # #         collection_name=collection_name,
# # # # # #         index_name=index_name
# # # # # #     )
# # # # # #     print(f"✅ Collection '{collection_name}' already exists.")

# # # # # #     # Store
# # # # # #     texts = [doc.page_content for doc in documents]
# # # # # #     metadatas = [doc.metadata for doc in documents]
# # # # # #     ids = [str(uuid4()) for _ in documents]
# # # # # #     vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
# # # # # #     print(f"[DEBUG] 📦 Stored {len(documents)} docs to MongoDB Atlas ({db_name}.{collection_name})")

# # # # # #     # Preview
# # # # # #     print("\n[DEBUG] 🧾 Sample Document Preview:")
# # # # # #     print(f"📄 page_content = {documents[0].page_content[:500]}")
# # # # # #     print(f"📎 metadata = {documents[0].metadata}")

# # # # # #     log_store_event(
# # # # # #         file_name=file_name,
# # # # # #         chunk_count=len(documents),
# # # # # #         status="stored",
# # # # # #         file_hash=file_hash,
# # # # # #         additional_info={"subject": subject_tag}
# # # # # #     )
# # # # # #     print(f"📝 Logged STORE event for: {file_name}")
# # # # # #     print("✅ STORE flow completed successfully!")

# # # # # # def store_multiple_files(file_paths, tag=None):
# # # # # #     for path in file_paths:
# # # # # #         try:
# # # # # #             store_to_mongodb(path, tag=tag)
# # # # # #         except Exception as e:
# # # # # #             print(f"❌ Failed to store {path}: {e}")

