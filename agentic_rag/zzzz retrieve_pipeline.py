# retrieve_pipeline.py

import os
from agentic_rag.retriever_factory import get_retriever_model
from agentic_rag.mongo_utils import load_mongo_config, connect_to_mongo
from agentic_rag.log_utils import log_retrieve_event, purge_old_logs
from datetime import timedelta, datetime
from langchain.chat_models import ChatOpenAI

# from langchain_core.documents import Document

def retrieve_answer(user_query: str, subject_hint: str = None):
    # 1. Load config and setup
    config = load_mongo_config()
    provider = os.getenv("EMBEDDING_PROVIDER", "gpt")
    retriever = get_retriever_model(provider)

    # 2. Detect subject or use hint
    # subject = detect_subject_from_query(user_query, subject_hint)
    subject = detect_subject_from_query(user_query, subject_hint, config)

    subject_config = config.get(subject)
    if not subject_config:
        print(f"[WARN] Subject '{subject}' not found in config. Falling back to 'default'.")
        subject = "default"
        subject_config = config.get(subject)

        if not subject_config:
            raise ValueError("[RETRIEVE ERROR] No valid subject config found (neither detected nor default).")

    index_name = subject_config.get("index_name", "default")
    collection_name = subject_config["collection_name"]

    # 3. Connect to MongoDB
    vector_collection = connect_to_mongo(collection_name)

    # 4. Retrieve matching documents (similarity search)
    # matched_docs: list[Document] = retriever.retrieve(user_query, vector_collection)
    matched_docs = retriever.retrieve(user_query, vector_collection, index_name=index_name)

    # 5. RAG Synthesis using LLM
    model_name = os.getenv("LLM_MODEL", "gpt-4")
    llm = ChatOpenAI(model_name=model_name, temperature=0)
    final_response = synthesize_with_llm(user_query, matched_docs, llm)


    # 6. Log the retrieve action
    log_retrieve_action(user_query, subject, len(matched_docs), provider)

    return final_response



# Optional: Add smart heuristics
def detect_subject_from_query(query: str, hint: str = None, config: dict = None):
    if hint:
        return hint.lower()

    lowered = query.lower()
    if "history" in lowered:
        return "history"
    if "profile" in lowered:
        return "profile"
    if "project" in lowered:
        return "projects"

    if config and "default" in config:
        return "default"

    raise ValueError("[RETRIEVE ERROR] Unable to detect subject and no fallback 'default' config found.")



def synthesize_with_llm(query, docs, llm):
    context = "\n\n".join([d.page_content for d in docs])
    prompt = f"""Answer the question based on the context below:
    Context: {context}

    Question: {query}
    """

    response = llm.invoke(prompt)
    return response.content.strip()


def log_retrieve_action(query, subject, num_results, provider):
    # 🧹 Step 1: Clean up logs older than 2 days
    cutoff_time = datetime.utcnow() - timedelta(days=2)
    purge_old_logs(cutoff_time)

    # 📝 Step 2: Log current query
    log_retrieve_event(query, subject, num_results, provider)
    print(f"[RETRIEVE] Logged + Cleaned | Query='{query}' | Subject={subject} | Matches={num_results} | Provider={provider}")



