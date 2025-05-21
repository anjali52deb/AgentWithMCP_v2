# agentic_rag_pipeline.py (placed under /routes/)

"""
Agentic-RAG Store and Retrieve implementation
- Supports dynamic LLM selection: OpenAI GPT or Google Gemini
- Modularized for LangGraph integration
- Supabase for metadata logging
- Pinecone for vector store
"""

import os
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

import pinecone
from datastore.supabase_client import get_logged_files, log_metadata

# Google Gemini (via LangChain integration)
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Init Pinecone + Embeddings ---
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment="us-west1-gcp")
embed_model = OpenAIEmbeddings()

# --- Helper: Create file hash ---
def generate_hash(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash

# --- Helper: Simple LLM classifier ---
def classify_chunk(content: str, llm_type: str = "gpt") -> str:
    if llm_type == "gpt":
        from langchain.llms import OpenAI
        llm = OpenAI(temperature=0)
    elif llm_type == "gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
    else:
        raise ValueError("Unsupported LLM type. Use 'gpt' or 'gemini'")

    return llm.predict(f"Classify this text into a domain tag: {content[:500]}")

# --- STORE Flow ---
def store_document(filepath: str, index_name: str, llm_type: str = "gpt"):
    file_hash = generate_hash(filepath)
    logged_files = get_logged_files()

    if file_hash in logged_files:
        print("⛔ File already stored. Skipping upload.")
        return

    # 1. Load document
    loader = PyPDFLoader(filepath)
    pages = loader.load()

    # 2. Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(pages)

    # 3. Optional classification
    for chunk in chunks:
        chunk.metadata['tag'] = classify_chunk(chunk.page_content, llm_type)

    # 4. Write to Pinecone
    Pinecone.from_documents(chunks, embed_model, index_name=index_name)

    # 5. Log metadata to Supabase
    log_metadata({
        "file_id": str(uuid.uuid4()),
        "file_hash": file_hash,
        "source": filepath,
        "index_used": index_name,
        "chunk_count": len(chunks),
        "timestamp": datetime.now().isoformat()
    })

    print("✅ Store pipeline complete.")


# --- RETRIEVE Flow ---
def retrieve_answer(query: str, index_name: str, llm_type: str = "gpt"):
    # 1. Query router (basic tag routing logic)
    if "finance" in query.lower():
        index_name = "rag_finance"
    elif "leave" in query.lower():
        index_name = "rag_hr_policy"
    # Else default to provided

    # 2. Vectorstore + retriever setup
    vectorstore = Pinecone.from_existing_index(index_name, embed_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # 3. LLM selector
    if llm_type == "gpt":
        llm = ChatOpenAI(model="gpt-3.5-turbo")
    elif llm_type == "gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
    else:
        raise ValueError("Unsupported LLM type. Use 'gpt' or 'gemini'")

    # 4. RAG synthesis
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    # 5. Run query
    result = qa(query)

    print("📋 Final Answer:", result['result'])
    print("📄 Source Chunks:")
    for doc in result['source_documents']:
        print("---", doc.page_content[:200])
