# retrieve_pipeline.py

from agentic_rag.mongo_client import get_mongo_vectorstore
from agentic_rag.index_router import route_index
from agentic_rag.llm_wrapper import get_llm_response
from agentic_rag.retrieve_logger import log_retrieve_event

def retrieve_from_mongodb(query: str, tag: str = None):
    print(f"🔍 Starting RETRIEVE for: '{query}' | tag: {tag or 'default'}")

    # Step 1: Get config
    config = route_index(tag or "default")
    index_name = config.get("index_name", "default")
    llm_model = config.get("llm", "gpt-4")
    top_k = config.get("top_k", 5)

    # Step 2: Connect to vector store
    vectorstore = get_mongo_vectorstore(index_name=index_name)
    results = vectorstore.similarity_search(query, k=top_k)

    print(f"✅ Retrieved {len(results)} chunks from MongoDB Atlas")

    # Step 3: Compose context
    context = "\n\n".join([doc.page_content for doc in results])

    # Step 4: Call LLM
    prompt = f"Use the following context to answer the question:\n\n{context}\n\nQ: {query}"
    answer = get_llm_response(prompt, model_name=llm_model)

    # Step 5: Log retrieval
    log_retrieve_event(
        query=query,
        result_count=len(results),
        source_index=index_name,
        llm_used=llm_model,
        response_summary=answer[:300]
    )

    return answer
