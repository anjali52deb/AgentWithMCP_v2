# master_rag_agent.py

"""
Central dispatcher for Agentic-RAG system
Determines whether input is a STORE or RETRIEVE task
Then calls corresponding pipeline with proper LLM & debug config
"""

from agentic_rag.store_pipeline import store_document
from agentic_rag.retrieve_pipeline import retrieve_answer
from agentic_rag.universal_loader import detect_request_type
from agentic_rag.utils import debug_log


def run_master_agent(input_data: str, is_file: bool, llm_type: str = "gpt", temperature: float = 0.3, debug: bool = False):
    """
    Agentic master dispatcher

    :param input_data: Filepath (for store) or text query (for retrieve)
    :param is_file: True for file input (store), False for query (retrieve)
    :param llm_type: 'gpt' or 'gemini'
    :param temperature: float for LLM creativity
    :param debug: if True, enable debug logs
    """

    if is_file:
        if debug:
            debug_log("🧾 Master Agent: Detected FILE → Routing to STORE pipeline")
        store_document(filepath=input_data, llm_type=llm_type, temperature=temperature, debug=debug)

    else:
        if debug:
            debug_log("🔍 Master Agent: Detected QUERY → Routing to RETRIEVE pipeline")
        retrieve_answer(query=input_data, llm_type=llm_type, temperature=temperature, debug=debug)
