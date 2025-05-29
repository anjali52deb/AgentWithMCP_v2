# subject_db_mapper.py

# ===== KEEP this for reference =====
# subject_to_db_map = {
#     "HR Policy": "RAG_HR_DB",
#     "Security": "RAG_Security_DB",
#     "Finance": "RAG_Finance_DB",
#     "Engineering": "RAG_Engg_DB",
#     "Sales": "RAG_Sales_DB",
#     "Legal": "RAG_Legal_DB"
# }


subject_to_db_map = {
    "CompanyProfile": "Profile_DB",
    "TransactionHistory": "History_DB",
    "EverythingElse": "Misc_DB"
}

# def get_db_for_subject(subject: str) -> str:
#     return subject_to_db_map.get(subject, "Misc_DB")

def get_db_and_collection_for_subject(subject: str) -> tuple:
    collection = subject_to_db_map.get(subject, "Misc_DB")
    return "agentic_rag", collection

