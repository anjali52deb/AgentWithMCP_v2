# subject_db_mapper.py
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
    "TrasactionHistory": "History_DB",
    "EverythingElse": "Misc_DB"
}

def get_db_for_subject(subject: str) -> str:
    return subject_to_db_map.get(subject, "RAG_Default_DB")
