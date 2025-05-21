# store_pipeline.py

"""
Handles RAG 'Store' Flow:
1. Load file and chunk
2. Classify each chunk (LLM)
3. Select proper index
4. Embed + store in Pinecone
5. Log metadata in Supabase
"""

from agentic_rag.universal_loader import load_file
from agentic_rag.llm_wrapper import classify_text
from agentic_rag.index_router import get_index_for_tag
from agentic_rag.store_logger import log_store_event
from agentic_rag.utils import debug_log

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
import os
import uuid
from datetime import datetime
import hashlib

# Init Pinecone once
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment="us-west1-gcp")
embed_model = OpenAIEmbeddings()


def store_document(filepath: str, llm_type: str = "gpt", temperature: float = 0.3, debug: bool = False):
    if debug:
        debug_log(f"📥 Starting STORE for file: {filepath}")

    # Step 1: Load and chunk
    documents = load_file(filepath)

    # Step 2: Classify and route
    for doc in documents:
        tag = classify_text(doc.page_content, llm_type=llm_type, temperature=temperature)
        doc.metadata['tag'] = tag
        index_name = get_index_for_tag(tag)

        if debug:
            debug_log(f"🏷️ Chunk classified as '{tag}' → Routing to index: {index_name}")

        # Step 3: Embed and store in Pinecone
        Pinecone.from_documents([doc], embed_model, index_name=index_name)

    # Step 4: Log metadata
    file_hash = _generate_hash(filepath)
    log_store_event({
        "file_id": str(uuid.uuid4()),
        "file_hash": file_hash,
        "source": filepath,
        "chunk_count": len(documents),
        "timestamp": datetime.now().isoformat()
    })

    if debug:
        debug_log("✅ Store pipeline completed.")


def _generate_hash(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
