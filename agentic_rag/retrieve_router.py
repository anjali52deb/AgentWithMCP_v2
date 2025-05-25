# retrieve_router.py

from agentic_rag.intent_classifier import classify_intent
from agentic_rag.subject_classifier import classify_subject
from agentic_rag.subject_db_mapper import get_db_for_subject
from agentic_rag.vectorstore_manager import get_vectorstore_instance

def retrieve_answer(query: str) -> str:
    intent = classify_intent(query)

    if intent != "RAG-Retrieve":
        return f"🛑 Query blocked. Detected intent: {intent}"

    subject = classify_subject(query)
    db_name = get_db_for_subject(subject)
    vectorstore = get_vectorstore_instance(db_name)

    results = vectorstore.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in results])
