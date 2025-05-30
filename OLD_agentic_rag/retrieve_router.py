# retrieve_router.py

from agentic_rag.intent_classifier import classify_intent
from agentic_rag.subject_classifier import classify_subject
from agentic_rag.vectorstore_manager import get_vectorstore_instance
from agentic_rag.retrieve_logger import log_retrieve_event
from agentic_rag.XXXdb_config import default_fallback_db


def retrieve_answer(query: str):
    print(f"\n🔹 Query: {query}")

    # Step 1: Intent Classification
    intent = classify_intent(query)
    print(f"Intent: {intent}")

    if intent != "RAG-Retrieve":
        print(f"🛑 Query blocked. Detected intent: {intent}")
        return f"🛑 Query blocked. Detected intent: \"{intent}\""

    # Step 2: Subject Classification
    subject = classify_subject(query)
    print(f"Subject: {subject}")

    # Subject → (db_name, collection_name)
    subject_to_db_map = {
        "CompanyProfile": ("agentic_rag", "Profile_DB"),
        "TransactionHistory": ("agentic_rag", "History_DB"),
        "EverythingElse": ("agentic_rag", "Misc_DB")
    }
    db_name = subject_to_db_map.get(subject, ("agentic_rag", "Misc_DB"))

    print(f"DB: {db_name}")

    # Step 3: Retrieve from subject-specific DB
    vectorstore = get_vectorstore_instance(db_name)
    results = vectorstore.similarity_search(query, k=3)

    # Log and show
    log_retrieve_event(
        query=query,
        intent=intent,
        subject=subject,
        db_name=db_name,
        result_count=len(results)
    )

    if results:
        print(f"Results found: {len(results)}")
        # for doc in results:
        #     print(doc.page_content.strip()[:800], "\n")
        seen = set()
        for doc in results:
            text = doc.page_content.strip()
            if text and text not in seen:
                print(text[:800], "\n")
                seen.add(text)        
        return "\n".join([doc.page_content.strip() for doc in results])

    print(f"🚫 No relevant results found in [{db_name}] or fallback.")
    print("Try rephrasing or uploading more relevant data.")

    # Fallback attempt
    if db_name != default_fallback_db:
        fallback_store = get_vectorstore_instance(default_fallback_db)
        results = fallback_store.similarity_search(query, k=3)

        log_retrieve_event(
            query=query,
            intent=intent,
            subject="Fallback",
            db_name=default_fallback_db,
            result_count=len(results)
        )

        if results:
            print(f"✅ Fallback returned {len(results)} results.")
            printed = set()
            for doc in results:
                snippet = doc.page_content.strip()
                if snippet and snippet not in printed:
                    print(snippet)
                    printed.add(snippet)
            # for doc in results:
            #     print(doc.page_content.strip()[:800], "\n")

            return "\n".join([doc.page_content.strip() for doc in results])

    return "❌ No results found in primary or fallback."



# =================================================================================
# =================================================================================

# from agentic_rag.intent_classifier import classify_intent
# from agentic_rag.subject_classifier import classify_subject
# from agentic_rag.subject_db_mapper import get_db_and_collection_for_subject
# from agentic_rag.vectorstore_manager import get_vectorstore_instance
# from agentic_rag.retrieve_logger import log_retrieve_event
# from agentic_rag.db_config import default_fallback_db

# def retrieve_answer(query: str) -> str:
#     intent = classify_intent(query)
#     print(f"Intent: {intent}")

#     if intent != "RAG-Retrieve":
#         return f"🛑 Query blocked. Detected intent: {intent}"

#     subject = classify_subject(query)
#     print(f"Subject: {subject}")

#     db_name = get_db_and_collection_for_subject(subject)
#     print(f"DB: {db_name}")

#     vectorstore = get_vectorstore_instance(db_name)
#     results = vectorstore.similarity_search(query, k=3)
#     print(f"Results found: {len(results)}")

#     # 📝 Always log — even if results are 0
#     log_retrieve_event(
#         query=query,
#         intent=intent,
#         subject=subject,
#         db_name=db_name,
#         result_count=len(results)
#     )

#     if not results:
#         fallback_db = "Misc_DB"
#         if db_name != fallback_db:
#             fallback_store = get_vectorstore_instance(fallback_db)
#             results = fallback_store.similarity_search(query, k=3)

#             # 🔁 Log fallback DB (optional - same query ID could be reused)
#             log_retrieve_event(
#                 query=query,
#                 intent=intent,
#                 subject="Fallback",
#                 db_name=fallback_db,
#                 result_count=len(results)
#             )

#             if results:
#                 return f"⚠️ No results in [{db_name}]. Showing from fallback [{fallback_db}]:\n\n" + "\n\n".join([doc.page_content for doc in results])

#         return f"🚫 No relevant results found in [{db_name}] or fallback.\nTry rephrasing or uploading more relevant data."

#     return "\n\n".join([doc.page_content for doc in results])




# =================================================================================
# =================================================================================
# WORKING COPY - 2nd version
# from agentic_rag.intent_classifier import classify_intent
# from agentic_rag.subject_classifier import classify_subject
# from agentic_rag.subject_db_mapper import get_db_for_subject
# from agentic_rag.vectorstore_manager import get_vectorstore_instance

# from agentic_rag.retrieve_logger import log_retrieve_event

# def retrieve_answer(query: str) -> str:
#     intent = classify_intent(query)
#     print(f"Intent: {intent}")

#     if intent != "RAG-Retrieve":
#         return f"🛑 Query blocked. Detected intent: {intent}"

#     subject = classify_subject(query)
#     db_name = get_db_for_subject(subject)
#     vectorstore = get_vectorstore_instance(db_name)
#     results = vectorstore.similarity_search(query, k=3)

#     print(f"Subject: {subject}")
#     print(f"DB: {db_name}")
#     print(f"Results found: {len(results)}")


#     if not results:
#         # Try fallback
#         fallback_db = "Misc_DB"
#         if db_name != fallback_db:
#             fallback_store = get_vectorstore_instance(fallback_db)
#             results = fallback_store.similarity_search(query, k=3)
#             if results:
#                 return f"⚠️ No results in [{db_name}]. Showing from fallback [{fallback_db}]:\n\n" + "\n\n".join([doc.page_content for doc in results])
        
#         return f"🚫 No relevant results found in [{db_name}] or fallback.\nTry rephrasing or uploading more relevant data."

#     return "\n\n".join([doc.page_content for doc in results])
# =================================================================================
# =================================================================================
# WORKING COPY - 1st version
# def retrieve_answer(query: str) -> str:
#     intent = classify_intent(query)
#     print(f"Intent: {intent}")

#     if intent != "RAG-Retrieve":
#         return f"🛑 Query blocked. Detected intent: {intent}"

#     subject = classify_subject(query)
#     print(f"Subject: {subject}")

#     db_name = get_db_for_subject(subject)
#     print(f"DB: {db_name}")

#     vectorstore = get_vectorstore_instance(db_name)
#     results = vectorstore.similarity_search(query, k=3)
#     print(f"Results found: {len(results)}")

#     return "\n\n".join([doc.page_content for doc in results])

