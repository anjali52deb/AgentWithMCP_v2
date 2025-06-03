# gemini_embedder.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiEmbeddings:
    def __init__(self, model_name="models/embedding-001"):
        self.model = genai.get_model(model_name)

    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            try:
                response = genai.embed_content(
                    model=self.model.name,  # ✅ correct usage
                    content=text,
                    task_type="retrieval_document",
                    title="DocChunk"
                )
                embeddings.append(response["embedding"])
            except Exception as e:
                print(f"❌ Gemini embedding failed: {e}")
                embeddings.append([0.0] * 768)  # fallback for error case
        return embeddings

    def embed_query(self, text):
        response = genai.embed_content(
            model=self.model.name,
            content=text,
            task_type="retrieval_query",
            title="Query"
        )
        return response["embedding"]
