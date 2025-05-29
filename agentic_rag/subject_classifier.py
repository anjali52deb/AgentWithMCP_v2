# subject_classifier.py
from typing import Optional
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SUBJECT_CANDIDATES = ["Profile_DB", "History_DB", "Misc_DB", ]
SUBJECT_CANDIDATES = [
    "CompanyProfile",
    "TransactionHistory",
    "EverythingElse"
]


def classify_subject(query: str) -> Optional[str]:
    prompt = f"""
You are a classifier agent. Given a user query, identify which of the following subjects it belongs to:
{', '.join(SUBJECT_CANDIDATES)}.

Query: "{query}"

Respond with only the subject name. If none match, return "Unknown".
"""
    response = client.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()
