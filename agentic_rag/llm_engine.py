# llm_wrapper.py

from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_llm_response(prompt: str, model_name: str = "gpt-4") -> str:
    # Simple switch based on model name
    if "gpt" in model_name:
        model = ChatOpenAI(model=model_name, temperature=0)
        return model.invoke(prompt).content  # ✅ Get actual string response

    elif "gemini" in model_name:
        # Placeholder
        return "Gemini LLM response (not implemented yet)"

    else:
        raise ValueError(f"❌ Unsupported model: {model_name}")



def split_text_into_chunks(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs = splitter.create_documents([text])
    return [doc.page_content for doc in docs]
