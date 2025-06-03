import os
from typing import Optional, List
from langchain_core.documents import Document
from agentic_rag.mongo_utils import load_mongo_config
from agentic_rag.retriever_factory import get_retriever_model
from agentic_rag.log_utils import log_retrieve_event, clean_logs_once_per_day
from langchain_openai import ChatOpenAI

# These would typically come from your actual store logic module:
from agentic_rag.attachment_handlers import load_file  # assumed function to load and chunk
from agentic_rag.embedding_factory import embed_and_store  # assumed function to embed and write to DB

class MasterRAGAgent:
    def __init__(self, embedding_provider: str = "gpt"):
        self.provider = embedding_provider.lower()
        self.config = load_mongo_config()
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    def run(self, query: Optional[str] = None, mode: str = "auto", file: Optional[str] = None):
        """
        Entry point. Determines mode and executes STORE or RETRIEVE.
        - mode: "auto", "store", "retrieve"
        """
        if mode == "store" or (mode == "auto" and file):
            return self.run_store(file)
        elif mode == "retrieve" or (mode == "auto" and query):
            return self.run_retrieve(query)
        else:
            raise ValueError("[RAG AGENT] Could not determine mode — please pass a query or file.")

    def run_store(self, file_path: str):
        print(f"[STORE] Processing file: {file_path}")
        # Step 1: Load and chunk file
        chunks, metadata = load_file(file_path)  # returns List[Document], metadata: Dict

        # Step 2: Classify subject (based on filename or content)
        subject = self.classify_subject(file_path, metadata)

        # Step 3: Embed and write to MongoDB
        embed_and_store(
            documents=chunks,
            subject=subject,
            provider=self.provider
        )

        print(f"[STORE] Stored {len(chunks)} chunks under subject '{subject}'")
        return f"✅ Stored {len(chunks)} chunks under subject '{subject}'"

    def run_retrieve(self, query: str):
        subject = self.detect_subject_from_query(query)
        retriever = get_retriever_model(subject, self.provider)

        try:
            matched_docs = retriever.invoke(query)
        except Exception as e:
            if "indexed with" in str(e) and "queried with" in str(e):
                raise RuntimeError(
                    f"❌ LLM embedding mismatch: Try correct provider for this index.") from e
            else:
                raise

        self.evaluate_retrieve_quality(matched_docs)
        final_answer = self.synthesize_with_llm(query, matched_docs)

        clean_logs_once_per_day()
        log_retrieve_event(query, subject, len(matched_docs), self.provider)

        return final_answer

    def detect_subject_from_query(self, query: str) -> str:
        lowered = query.lower()
        if "history" in lowered:
            return "history"
        elif "profile" in lowered:
            return "profile"
        elif any(x in lowered for x in ["index", "mongodb", "vector"]):
            return "default"
        return "default"

    def classify_subject(self, file_path: str, metadata: dict) -> str:
        filename = os.path.basename(file_path).lower()
        if any(key in filename for key in ["emp", "profile", "cv"]):
            return "profile"
        elif any(key in filename for key in ["history", "log", "trans"]):
            return "history"
        return "default"

    def synthesize_with_llm(self, query: str, docs: List[Document]) -> str:
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = f"""
        You are a helpful assistant. Based on the following context, answer the user query.
        Context: {context}

        Question: {query}
        If the context partially answers the question, summarize the available insights confidently.
        """
        return self.llm.invoke(prompt).content.strip()

    def evaluate_retrieve_quality(self, docs: List[Document]):
        print(f"[EVAL] Retrieved {len(docs)} docs")
        # Future: calculate average score, threshold % match, chunk diversity
        for i, doc in enumerate(docs):
            print(f"- Chunk {i+1}: {doc.page_content[:100]}...")
