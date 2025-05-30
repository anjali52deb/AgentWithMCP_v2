# subject_db_mapper.py

subject_to_db_map = {
    "CompanyProfile": "Profile_DB",
    "TransactionHistory": "History_DB",
    "EverythingElse": "Misc_DB"
}

def get_db_and_collection_for_subject(subject: str) -> tuple:
    collection = subject_to_db_map.get(subject, "Misc_DB")
    return "agentic_rag", collection

