# # store_pipeline.py


import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uuid import uuid4
from dotenv import load_dotenv

from langchain.schema.document import Document as LangDocument

from agentic_rag.store_index_utils import ensure_collection_exists
from agentic_rag.subject_classifier import classify_subject
from agentic_rag.LLM_LangChain import split_text_into_chunks
from agentic_rag.attachment_handlers import extract_text_from_file
from agentic_rag.mongo_client import get_mongo_vectorstore, get_mongo_client
from agentic_rag.store_logger import log_store_event
from agentic_rag.utils import get_file_hash
from agentic_rag.subject_db_mapper import get_db_and_collection_for_subject

load_dotenv()

def store_to_mongodb(file_path: str, tag: str = "default"):
    print(f"\n📥 Starting STORE for file: {file_path} | tag: {tag}")

    file_name = os.path.basename(file_path)
    subject = classify_subject(file_name)
    db_name, collection_name = get_db_and_collection_for_subject(subject)
    index_name = f"vector_index_{collection_name.lower()}"
    file_hash = get_file_hash(file_path)

    # ✅ Deduplication check
    mongo_client = get_mongo_client()
    collection = mongo_client[db_name][collection_name]
    if collection.find_one({ "metadata.file_hash": file_hash }):
        print(f"⚠️ File already stored (hash match): {file_name}. Skipping.")
        return

    # Step 1: Extract + Chunk
    extracted_text = extract_text_from_file(file_path)
    if not extracted_text:
        print("❌ No text extracted from file. Aborting.")
        return

    text_chunks = split_text_into_chunks(extracted_text)
    print(f"[DEBUG] 📄 Extracted into {len(text_chunks)} chunks")

    # Step 2: Create LangChain Documents (page_content + metadata)
    documents = []
    for chunk in text_chunks:
        if chunk:
            documents.append(
                LangDocument(
                    page_content=chunk,
                    metadata={
                        "source": file_name,
                        "text": chunk,
                        "file_hash": file_hash
                    }
                )
            )

    if not documents:
        print("❌ No valid documents to store. Aborting.")
        return

    # Step 3: Ensure collection and index
    ensure_collection_exists(db_name=db_name, collection_name=collection_name)

    # Step 4: Store to MongoDB Vector Store
    vectorstore = get_mongo_vectorstore(
        index_name=index_name,
        db_name=db_name,
        collection_name=collection_name
    )
    print(f"[DEBUG] 📦 Storing {len(documents)} docs to MongoDB Atlas ({db_name}.{collection_name})")

    print("\n[DEBUG] 🧾 Sample Document Preview:")
    print("📄 page_content =", documents[0].page_content)
    print("📎 metadata =", documents[0].metadata)


    vectorstore.add_documents(documents=documents)

    # Step 5: Log the event
    log_store_event(
        file_name=file_name,
        chunk_count=len(documents),
        status="success",
        file_hash=file_hash
    )

    print("✅ STORE flow completed successfully!")


def store_multiple_files(file_paths: list, tag: str = "default"):
    for path in file_paths:
        try:
            store_to_mongodb(path, tag)
        except Exception as e:
            print(f"❌ Failed to store {path}: {str(e)}")






# # ====================================================================================
# # ====================================================================================
# import os
# import sys
# from uuid import uuid4
# from dotenv import load_dotenv

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from agentic_rag.store_index_utils import ensure_collection_exists
# from agentic_rag.subject_classifier import classify_subject
# from agentic_rag.LLM_LangChain import split_text_into_chunks
# from agentic_rag.attachment_handlers import extract_text_from_file
# from agentic_rag.mongo_client import get_mongo_vectorstore
# from agentic_rag.store_logger import log_store_event
# from agentic_rag.utils import get_file_hash
# from agentic_rag.subject_db_mapper import get_db_and_collection_for_subject

# from langchain.schema.document import Document as LangDocument
# from langchain.docstore.document import Document

# load_dotenv()

# def generate_doc_objects(text_chunks, metadata=None):
#     return [
#         Document(page_content=chunk, metadata=metadata or {})
#         for chunk in text_chunks
#     ]

# def store_to_mongodb(file_path: str, tag: str = "default"):
#     from langchain.schema.document import Document as LangDocument

#     print(f"\n📥 Starting STORE for file: {file_path} | tag: {tag}")

#     file_name = os.path.basename(file_path)
#     subject = classify_subject(file_name)
#     db_name, collection_name = get_db_and_collection_for_subject(subject)
#     index_name = f"vector_index_{collection_name.lower()}"

#     # Step 1: Extract + Chunk
#     extracted_text = extract_text_from_file(file_path)
#     if not extracted_text:
#         print("❌ No text extracted from file. Aborting.")
#         return

#     text_chunks = split_text_into_chunks(extracted_text)
#     print(f"[DEBUG] 📄 Extracted into {len(text_chunks)} chunks")

#     # Step 2: Build documents (directly, without relying on external doc list)
#     documents = []
#     for chunk in text_chunks:
#         if chunk:  # Only add if chunk is not empty
#             doc = LangDocument(
#                 page_content=chunk,
#                 metadata={
#                     "source": file_name,
#                     "text": chunk
#                 }
#             )
#             documents.append(doc)

#     if not documents:
#         print("❌ No valid documents to store. Aborting.")
#         return

#     # Step 3: Ensure collection exists
#     ensure_collection_exists(db_name=db_name, collection_name=collection_name)

#     # Step 4: Store in Vector DB
#     vectorstore = get_mongo_vectorstore(
#         index_name=index_name,
#         db_name=db_name,
#         collection_name=collection_name
#     )
#     print(f"[DEBUG] 📦 Storing {len(documents)} docs to MongoDB Atlas ({db_name}.{collection_name})")
#     vectorstore.add_documents(documents=documents)

#     # Step 5: Log event
#     file_hash = get_file_hash(file_path)
#     log_store_event(
#         file_name=file_name,
#         chunk_count=len(documents),
#         status="success",
#         file_hash=file_hash
#     )

#     print("✅ STORE flow completed successfully!")


# def store_multiple_files(file_paths: list, tag: str = "default"):
#     for path in file_paths:
#         try:
#             store_to_mongodb(path, tag)
#         except Exception as e:
#             print(f"❌ Failed to store {path}: {str(e)}")

# # ====================================================================================
# # ====================================================================================
# import os
# import sys
# from uuid import uuid4
# from dotenv import load_dotenv

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# from agentic_rag.store_index_utils import ensure_collection_exists
# from agentic_rag.subject_classifier import classify_subject

# from agentic_rag.LLM_LangChain import split_text_into_chunks
# from agentic_rag.attachment_handlers import extract_text_from_file
# from agentic_rag.mongo_client import get_mongo_vectorstore
# from agentic_rag.index_router import route_index
# from agentic_rag.store_logger import log_store_event
# from agentic_rag.utils import get_file_hash

# from agentic_rag.subject_classifier import classify_subject
# from agentic_rag.subject_db_mapper import get_db_and_collection_for_subject

# from langchain.docstore.document import Document
# from langchain.schema.document import Document as LangDocument

# load_dotenv()

# def generate_doc_objects(text_chunks, metadata=None):
#     return [
#         Document(page_content=chunk, metadata=metadata or {})
#         for chunk in text_chunks
#     ]

# def store_to_mongodb(file_path: str, tag: str = "default"):
#     print(f"📥 Starting STORE for file: {file_path} | tag: {tag}")

#     # config = route_index(tag)
#     # db_name = config.get("db_name")
#     # collection_name = config.get("collection_name")
#     # index_name = config.get("index_name")

#     # subject = classify_subject(os.path.basename(file_path))
#     # db_name = get_db_for_subject(subject)

#     file_name = os.path.basename(file_path)  # ✅ ADD THIS LINE
#     subject = classify_subject(file_name)
#     # db_name = get_db_for_subject(subject)
#     # collection_name = db_name  # assuming collection = db

#     db_name, collection_name = get_db_and_collection_for_subject(subject)

#     index_name = f"vector_index_{db_name.lower()}"  # or use fixed if needed


#     extracted_text = extract_text_from_file(file_path)
#     if not extracted_text:
#         print("❌ No text extracted from file. Aborting.")
#         return

#     text_chunks = split_text_into_chunks(extracted_text)
#     print(f"[DEBUG] 📄 Extracted into {len(text_chunks)} chunks")

#     metadata = {"source": os.path.basename(file_path)}
#     documents = generate_doc_objects(text_chunks, metadata=metadata)

#     # ✅ Ensure the target collection exists (avoids failure if new)
#     ensure_collection_exists(db_name=db_name, collection_name=collection_name)

#     vectorstore = get_mongo_vectorstore(
#         index_name=index_name,
#         db_name=db_name,
#         collection_name=collection_name
#     )

#     print(f"[DEBUG] 📦 Storing {len(documents)} docs to MongoDB Atlas ({db_name}.{collection_name})")

#     # ✅ This is the correct, safe way:
#     # texts = [doc.page_content for doc in documents]
#     # metadatas = [doc.metadata for doc in documents]
#     # doc_ids = [str(uuid4()) for _ in documents]
#     # vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=doc_ids)

#     # Ensure clean format for Mongo
#     docs_to_store = [
#         LangDocument(page_content=doc.page_content, metadata=doc.metadata)
#         for doc in documents
#     ]

#     vectorstore.add_documents(documents=docs_to_store)



#     file_hash = get_file_hash(file_path)
#     log_store_event(
#         file_name=os.path.basename(file_path),
#         chunk_count=len(documents),
#         status="success",
#         file_hash=file_hash
#     )

#     print("✅ STORE flow completed successfully!")


# def store_multiple_files(file_paths: list, tag: str = "default"):
#     for path in file_paths:
#         try:
#             store_to_mongodb(path, tag)
#         except Exception as e:
#             print(f"❌ Failed to store {path}: {str(e)}")
