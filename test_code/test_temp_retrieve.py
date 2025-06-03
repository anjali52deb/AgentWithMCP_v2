import os
from pymongo import MongoClient
from langchain_core.documents import Document

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch

from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Constants (Hardcoded for this test)
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "agentic_rag"
COLLECTION_NAME = "Misc_DB"
INDEX_NAME = "vector_index_misc_db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
K = 5  # top-k documents

# 3. Environment setup
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 4. MongoDB connection
mongo_client = MongoClient(MONGO_URI)
collection = mongo_client[DB_NAME][COLLECTION_NAME]

print(f"[DEBUG] Using DB={DB_NAME}, Collection={COLLECTION_NAME}, Index={INDEX_NAME}")


# 5. Embedding + Vector Store
embedding_model = OpenAIEmbeddings()
vectorstore = MongoDBAtlasVectorSearch(
    collection,
    embedding_model,
    index_name=INDEX_NAME,
    text_key="chunk_text"
)

# 6. LLM setup
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# 7. Document retrieval
def retrieve_documents(query: str):
    docs_and_scores = vectorstore.similarity_search_with_score(query, k=K)
    print(f"\n🔎 Top Matches for Query: '{query}'\n")
    for i, (doc, score) in enumerate(docs_and_scores, start=1):
        print(f"Match #{i} | Score: {score:.4f}\nChunk: {doc.page_content}\n")

   
    return [doc for doc, _ in docs_and_scores]

# 8. Synthesize final answer
def synthesize_answer(query: str, documents: list[Document]):
    context = "\n\n".join([doc.page_content for doc in documents])

    prompt = f"""
        You are a helpful assistant. Based on the following context, answer the user query.
        Context: {context}

        Question: {query}
        If the context partially answers the question, summarize the available insights confidently. Avoid hallucination, but do not say “Not enough information” if clues are present.
        """
    response = llm.invoke(prompt)
    return response.content.strip()

# 9. Execute test
if __name__ == "__main__":
    user_query = "What is the new MongoDB index configuration update?"

    matched_docs = retrieve_documents(user_query)
    final_response = synthesize_answer(user_query, matched_docs)
    print("\n✅ Final Answer:\n", final_response)


