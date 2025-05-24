# retrieve_pipeline.py

"""
Handles RAG 'Retrieve' Flow:
1. Classify query
2. Route to proper index
3. Retrieve relevant chunks
4. LLM synthesis with GPT or Gemini
5. Return + optionally log output
"""

from agentic_rag.llm_wrapper import get_llm, classify_text
from agentic_rag.index_router import get_index_for_tag
from agentic_rag.retrieve_logger import log_retrieve_event
from agentic_rag.utils import debug_log

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain.chains import RetrievalQA
from pinecone import Pinecone

import os
from datetime import datetime

# Init Pinecone client with SDK v3+
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
embed_model = OpenAIEmbeddings(model="text-embedding-3-small")


def retrieve_answer(query: str, llm_type: str = "gpt", temperature: float = 0.3, debug: bool = False):
    if debug:
        debug_log(f"🔍 Starting RETRIEVE for query: {query}")

    # Step 1: Classify query
    tag = classify_text(query, llm_type, temperature)
    index_name = get_index_for_tag(tag)

    if debug:
        debug_log(f"🏷️ Query classified as '{tag}' → Using index: {index_name}")

    # Step 2: Retrieve from Pinecone
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embed_model,
        pinecone_client=pc
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Step 3: LLM synthesis
    llm = get_llm(llm_type, temperature)
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    result = qa(query)

    # Step 4: Log & return
    log_retrieve_event({
        "query": query,
        "index_used": index_name,
        "timestamp": datetime.now().isoformat(),
        "response": result['result']
    })

    print("\n📋 Final Answer:", result['result'])
    print("\n📄 Source Chunks:")
    for doc in result['source_documents']:
        print("---", doc.page_content[:200])
