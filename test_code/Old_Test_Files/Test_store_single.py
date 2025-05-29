import sys
import os
from dotenv import load_dotenv
from pprint import pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from agentic_rag.retrieve_router import retrieve_answer


# test_store_single.py
# from agentic_rag.store_pipeline import store_to_mongodb

# file_path = "_Data/employee_policy.pdf"  # Update if needed
# store_to_mongodb(file_path, tag="HRPolicy")

# test_store_multi.py
from agentic_rag.store_pipeline import store_multiple_files

file_list = [
    "_Data/employee_policy.pdf",
    "_Data/finance_policy.pdf",
    "_Data/security_guidelines.pdf"
]

store_multiple_files(file_list, tag="BatchHR")

