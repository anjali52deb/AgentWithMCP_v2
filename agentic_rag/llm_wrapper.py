# llm_wrapper.py

"""
LLM utility wrapper
- Supports GPT (OpenAI) and Gemini (Google)
- Accepts model name and temperature
- Also supports classification calls
"""

from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(llm_type: str = "gpt", temperature: float = 0.3, model_name: str = None):
    if llm_type == "gpt":
        model = model_name or "gpt-3.5-turbo"
        return ChatOpenAI(model=model, temperature=temperature)

    elif llm_type == "gemini":
        model = model_name or "gemini-pro"
        return ChatGoogleGenerativeAI(model=model, temperature=temperature)

    else:
        raise ValueError("❌ Unsupported LLM type. Use 'gpt' or 'gemini'")


def classify_text(text: str, llm_type: str = "gpt", temperature: float = 0.0):
    llm = get_llm(llm_type, temperature)
    prompt = f"Classify this text into a domain tag: {text[:500]}"
    return llm.predict(prompt)