# test_code/test_search_agent.py

# python test_code/test_search_agent.py
# Or with pytest:: pytest test_code/test_search_agent.py -s

# requirements.txt
# langchain
# openai
# serpapi
# requests
# beautifulsoup4
# pymupdf


import sys
import os
sys.path.append(os.path.abspath("../financial_agent"))

from mcp_server.routes.financial_web_search import run_financial_search

def test_apple_q2_2024():
    print("✅ Testing Apple Q2 2024 Report Search")
    result = run_financial_search(
        company="Apple",
        document_type="Quarterly Report",
        quarter="Q2",
        year="2024"
    )
    print(result)
    assert "Revenue" in result or "error" in result

def test_basf_q4_2023():
    print("✅ Testing BASF Q4 2023 Report Search")
    result = run_financial_search(
        company="BASF",
        document_type="Quarterly Report",
        quarter="Q4",
        year="2023",
        site="basf.com"
    )
    print(result)
    assert "Net Income" in result or "error" in result

if __name__ == "__main__":
    test_apple_q2_2024()
    test_basf_q4_2023()
