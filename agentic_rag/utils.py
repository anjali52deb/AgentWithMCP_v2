# utils.py

"""
Utility functions shared across Agentic-RAG modules
"""

import hashlib
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def debug_log(message: str):
    print(f"[DEBUG] {message}")

def get_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    return hashlib.md5(file_bytes).hexdigest()


def load_and_split_file(filepath, chunk_size=500):
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    return chunks

def guess_subject_tag(filename: str) -> str:
    filename_lower = filename.lower()
    if "finance" in filename_lower or "transaction" in filename_lower:
        return "TransactionHistory"
    elif "employee" in filename_lower or "hr" in filename_lower:
        return "CompanyProfile"
    else:
        return "Misc"
