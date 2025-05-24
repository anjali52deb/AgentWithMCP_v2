# universal_loader.py

"""
Loads different file formats for RAG Store pipeline:
Supports: PDF, TXT, JSON, HTML (basic)
Returns: List[Document] objects
"""
# NEW (recommended)
from langchain_community.document_loaders import PyPDFLoader, TextLoader, JSONLoader, UnstructuredHTMLLoader
from langchain.schema import Document
import os


def load_file(filepath: str) -> list[Document]:
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return PyPDFLoader(filepath).load()

    elif ext == ".txt":
        return TextLoader(filepath).load()

    elif ext == ".json":
        return JSONLoader(filepath).load()

    elif ext == ".html":
        return UnstructuredHTMLLoader(filepath).load()

    else:
        raise ValueError(f"❌ Unsupported file format: {ext}")
