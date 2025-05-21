# User ↔️ LangChain Agent
#    ↕
# LLM PromptTemplate + Memory
#    ↕
# Search Plan → SerpAPI → Scraper → Extractor
#    ↕
# Formatted Output (JSON or Text)


# pip install langchain openai serpapi requests beautifulsoup4 pymupdf


import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from serpapi import GoogleSearch
import requests, fitz, re
from bs4 import BeautifulSoup

# ---- 🔐 Set your API keys ----
os.environ["OPENAI_API_KEY"] = "your_openai_key"
os.environ["SERPAPI_API_KEY"] = "your_serpapi_key"

# ---- 🎯 LangChain Prompt Template ----
query_prompt = PromptTemplate(
    input_variables=["company", "document_type", "quarter", "year", "site"],
    template="Search for {company}'s {quarter} {year} {document_type} on {site}"
)

# ---- 🧠 Conversation Memory ----
memory = ConversationBufferMemory(input_key="company", memory_key="chat_history")

# ---- 💬 Language Model ----
llm = OpenAI(temperature=0)
chain = LLMChain(llm=llm, prompt=query_prompt, memory=memory)

# ---- 🔍 Search Function ----
def serp_search(query):
    search = GoogleSearch({
        "q": query,
        "api_key": os.environ["SERPAPI_API_KEY"],
        "num": 5
    })
    results = search.get_dict()
    return [r["link"] for r in results.get("organic_results", []) if "link" in r]

# ---- 📄 PDF Extractor ----
def extract_from_pdf(url):
    pdf_bytes = requests.get(url).content
    with open("temp.pdf", "wb") as f:
        f.write(pdf_bytes)
    doc = fitz.open("temp.pdf")
    text = "".join([page.get_text() for page in doc])
    return extract_financial_data(text, url)

# ---- 🌐 HTML Extractor ----
def extract_from_html(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    return extract_financial_data(text, url)

# ---- 🧾 Financial Metric Extractor ----
def extract_financial_data(text, url):
    def match(pattern): return re.search(pattern, text, re.IGNORECASE)
    return {
        "Company": match(r"(Apple|BASF)") and match(r"(Apple|BASF)").group(),
        "Quarter": match(r"(Q[1-4])\s?20\d{2}") and match(r"(Q[1-4])\s?20\d{2}").group(),
        "Year": match(r"Q[1-4]\s?(20\d{2})") and match(r"Q[1-4]\s?(20\d{2})").group(1),
        "Revenue": match(r"Revenue[^$\n]*\$\s?([\d.,]+[MB]?)") and match(r"Revenue[^$\n]*\$\s?([\d.,]+[MB]?)").group(1),
        "Net Income": match(r"Net Income[^$\n]*\$\s?([\d.,]+[MB]?)") and match(r"Net Income[^$\n]*\$\s?([\d.,]+[MB]?)").group(1),
        "EPS": match(r"(?:EPS|Earnings per Share)[^\d]*([\d.]+)") and match(r"(?:EPS|Earnings per Share)[^\d]*([\d.]+)").group(1),
        "Link to Full Report": url
    }

# ---- 🤖 Main LangChain Wrapper ----
def search_financials_with_memory(company, document_type, quarter, year, site="investor.apple.com"):
    query = chain.run(company=company, document_type=document_type, quarter=quarter, year=year, site=site)
    print(f"🔍 Query Generated: {query}")
    urls = serp_search(query)

    for url in urls:
        try:
            if url.lower().endswith(".pdf"):
                return extract_from_pdf(url)
            else:
                return extract_from_html(url)
        except Exception as e:
            print(f"❌ Failed on {url}: {e}")
            continue
    return {"error": "No valid financial report found."}

# At bottom of search_agent.py
def run_financial_search(company, document_type, quarter, year):
    return search_financials_with_memory(company, document_type, quarter, year)
