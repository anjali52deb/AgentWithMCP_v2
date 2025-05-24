# utils.py

"""
Utility functions shared across Agentic-RAG modules
"""

import hashlib

def debug_log(message: str):
    print(f"[DEBUG] {message}")

def get_file_hash(file_path: str) -> str:
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    return hashlib.md5(file_bytes).hexdigest()
