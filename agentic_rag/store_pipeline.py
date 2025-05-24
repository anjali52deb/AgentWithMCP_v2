# store_pipeline.py (Aligned with LangChain RAG Tutorial)

"""
RAG 'Store' pipeline aligned with official LangChain tutorial:
- LOAD → SPLIT → EMBED → STORE
- Uses RecursiveCharacterTextSplitter
- Embeds via OpenAI
- Batch inserts to Pinecone
- Compatible with direct host API key
"""

from agentic_rag.universal_loader import load_file
from agentic_rag.llm_wrapper import classify_text
from agentic_rag.index_router import get_index_for_tag
from agentic_rag.store_logger import log_store_event
from agentic_rag.utils import debug_log

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import pinecone
import os
import uuid
from datetime import datetime
import hashlib

# Pinecone Init via direct host
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    host="https://agentic-rag-dense-7xwqw04.svc.aped-4627-b74a.pinecone.io"
)

embed_model = OpenAIEmbeddings(model="text-embedding-3-small")


def store_document(filepath: str, llm_type: str = "gpt", temperature: float = 0.3, debug: bool = False):
    if debug:
        debug_log(f"📥 Starting STORE for file: {filepath}")

    raw_documents = load_file(filepath)  # returns list of Documents

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    all_chunks = splitter.split_documents(raw_documents)

    if debug:
        debug_log(f"📄 Loaded {len(raw_documents)} docs → {len(all_chunks)} chunks after splitting")

    for chunk in all_chunks:
        tag = classify_text(chunk.page_content, llm_type=llm_type, temperature=temperature)
        chunk.metadata['tag'] = tag

    # Group by tag/index to store in batch
    index_chunks_map = {}
    for chunk in all_chunks:
        index_name = get_index_for_tag(chunk.metadata['tag'])
        index_chunks_map.setdefault(index_name, []).append(chunk)

    for index_name, chunks in index_chunks_map.items():
        if debug:
            debug_log(f"🔃 Storing {len(chunks)} chunks → {index_name}")

        index = pinecone.Index(index_name)

        vectorstore = PineconeVectorStore(
            index=index,
            embedding=embed_model,
            text_key="page_content",
            namespace=""
        )

        vectorstore.add_documents(chunks)

    file_hash = _generate_hash(filepath)
    log_store_event({
        "file_id": str(uuid.uuid4()),
        "file_hash": file_hash,
        "source": filepath,
        "chunk_count": len(all_chunks),
        "timestamp": datetime.now().isoformat()
    })

    if debug:
        debug_log("✅ STORE pipeline completed successfully.")


def _generate_hash(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
