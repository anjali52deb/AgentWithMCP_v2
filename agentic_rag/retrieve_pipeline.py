# retrieve_pipeline.py


import os
from agentic_rag.retriever_factory import get_retriever_model
from agentic_rag.mongo_utils import load_mongo_config
from agentic_rag.log_utils import log_retrieve_event, purge_old_logs
from datetime import timedelta, datetime
from langchain_openai import ChatOpenAI  # ✅ Updated import


def retrieve_answer(user_query: str, subject_hint: str = None):
    # 1. Load config and setup
    config = load_mongo_config()
    provider = os.getenv("EMBEDDING_PROVIDER", "gpt")

    # 2. Detect subject or use hint
    subject = detect_subject_from_query(user_query, subject_hint, config)
    subject_config = config.get(subject)

    if not subject_config:
        print(f"[WARN] Subject '{subject}' not found in config. Falling back to 'default'.")
        subject = "default"
        subject_config = config.get(subject)

        if not subject_config:
            raise ValueError("[RETRIEVE ERROR] No valid subject config found (neither detected nor default).")

    # 3. Get retriever (handles index, collection internally)
    retriever = get_retriever_model(subject, provider)

    # 4. Retrieve documents from vector DB
    matched_docs = retriever.get_relevant_documents(user_query)

    print(f"[DEBUG] Matched {len(matched_docs)} docs")
    for doc in matched_docs:
        print("-", doc.page_content[:100])


    # 5. Synthesize final answer
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    final_response = synthesize_with_llm(user_query, matched_docs, llm)

    # 6. Log retrieve event
    log_retrieve_action(user_query, subject, len(matched_docs), provider)

    return final_response


def detect_subject_from_query(query: str, hint: str = None, config: dict = None):
    if hint:
        return hint.lower()

    lowered = query.lower()

    if "history" in lowered:
        return "history"
    elif "profile" in lowered:
        return "profile"
    
    # ⚠️ Originally sent to 'profile', but chunk is in 'default'
    elif "index" in lowered or "mongodb" in lowered or "vector" in lowered:
        return "default"  # ✅ This is where your chunk actually lives

    elif config and "default" in config:
        return "default"
    else:
        return "unknown"





def synthesize_with_llm(query: str, docs, llm):
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
    You are a helpful assistant. Based on the following context, answer the user query.
    Context: {context}

    Question: {query}
    If the context partially answers the question, summarize the available insights confidently. Avoid hallucination, but do not say “Not enough information” if clues are present.
    """

    response = llm.invoke(prompt)
    return response.content.strip()


def log_retrieve_action(query, subject, num_results, provider):
    cutoff_time = datetime.utcnow() - timedelta(days=2)
    purge_old_logs(cutoff_time)
    log_retrieve_event(query, subject, num_results, provider)
    print(f"[RETRIEVE] Logged + Cleaned | Query='{query}' | Subject={subject} | Matches={num_results} | Provider={provider}")
