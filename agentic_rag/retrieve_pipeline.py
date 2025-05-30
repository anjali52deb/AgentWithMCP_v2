# retrieve_pipeline.py

from agentic_rag.mongo_client import get_mongo_vectorstore
from agentic_rag.index_router import route_index
from agentic_rag.llm_engine import get_llm_response
from agentic_rag.logger import log_retrieve_event

def extract_doc_text(doc):
    """Robust method to get document content for prompt construction."""
    if hasattr(doc, "page_content") and isinstance(doc.page_content, str):
        return doc.page_content
    if hasattr(doc, "text"):
        return doc.text
    if "text" in doc.__dict__:
        return doc.__dict__["text"]
    if "text" in getattr(doc, "metadata", {}):
        return doc.metadata["text"]
    return "[❌ Unable to extract text]"

def retrieve_from_mongodb(query: str, tag: str = "default"):
    print(f"🔍 Starting RETRIEVE for: '{query}' | tag: {tag}")

    config = route_index(tag)
    db_name = config.get("db_name")
    collection_name = config.get("collection_name")
    index_name = config.get("index_name")
    top_k = config.get("top_k", 5)
    llm_model = config.get("llm", "gpt-4")

    vectorstore = get_mongo_vectorstore(
        index_name=index_name,
        db_name=db_name,
        collection_name=collection_name
    )

    #### What is the difference between these two lines?????????????????????
    results = vectorstore.similarity_search(query, k=top_k)
    # results = vectorstore.max_marginal_relevance_search(query, k=top_k, fetch_k=10)

    print(f"✅ Retrieved {len(results)} chunks from {db_name}.{collection_name}")


    if results:
        print(f"🧠 Raw doc sample keys: {list(vars(results[0]).keys())}")
    else:
        print("⚠️  No matching chunks found. Skipping LLM call.")
        return "⛔ No relevant content found in the vector database."

    for i, doc in enumerate(results):
        content = extract_doc_text(doc)
        print(f"\n📄 MATCH {i+1}:\n{content[:200]}")

    # Build prompt from extracted content
    context = "\n\n".join([extract_doc_text(doc) for doc in results])
    prompt = f"Use the following context to answer the question:\n\n{context}\n\nQ: {query}"

    # LLM call
    answer = get_llm_response(prompt, model_name=llm_model)

    # Logging
    log_retrieve_event(
        query=query,
        result_count=len(results),
        source_index=index_name,
        llm_used=llm_model,
        response_summary=answer[:300]
    )

    return answer

