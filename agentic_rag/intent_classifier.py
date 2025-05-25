# intent_classifier.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_intent(query: str) -> str:
    prompt = f"""
You are an intent classifier for an AI assistant. Given a query, classify the user's intent into one of:

- "RAG-Retrieve" (if it's asking a question that needs memory or stored knowledge)
- "Chitchat" (casual talk, jokes, greetings, etc.)
- "Tool-Use" (asking for a file conversion, summary, video/audio processing)
- "Unknown" (not clear)

Query: "{query}"

Just reply with one label from above.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()
