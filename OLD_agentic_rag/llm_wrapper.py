# llm_wrapper.py

# from langchain.chat_models import ChatOpenAI
# For Gemini support, import your Gemini wrapper here
from langchain_openai import ChatOpenAI

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




# # llm_wrapper.py

# """
# LLM utility wrapper
# - Supports GPT (OpenAI) and Gemini (Google)
# - Accepts model name and temperature
# - Also supports classification calls
# """

# from langchain.chat_models import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI


# def get_llm(llm_type: str = "gpt", temperature: float = 0.3, model_name: str = None):
#     if llm_type == "gpt":
#         model = model_name or "gpt-4"
#         return ChatOpenAI(model=model, temperature=temperature)

#     elif llm_type == "gemini":
#         model = model_name or "gemini-pro"
#         return ChatGoogleGenerativeAI(model=model, temperature=temperature)

#     else:
#         raise ValueError("❌ Unsupported LLM type. Use 'gpt' or 'gemini'")


# def classify_text(text: str, llm_type: str = "gpt", temperature: float = 0.0):
#     llm = get_llm(llm_type, temperature)
#     prompt = f"Classify this text into a domain tag: {text[:500]}"
#     return llm.predict(prompt)