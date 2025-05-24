import os
from dotenv import load_dotenv
load_dotenv()
import pinecone
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain.text_splitter import CharacterTextSplitter

pinecone_api_key = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

index_name = "agentic-rag-dense"
host = "https://agentic-rag-dense-7xwqw04.svc.aped-4627-b74a.pinecone.io"

# --- 1. Pinecone Initialization ---
try:
    pinecone.init(api_key=pinecone_api_key)
    print("Pinecone initialized successfully.")
except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    exit()

# --- 2. Prepare Data ---
raw_document_content = """
The quick brown fox jumps over the lazy dog. This is a sample document
to demonstrate storing data in Pinecone using LangChain and OpenAI embeddings.
Vector databases are essential for semantic search and RAG applications.
"""
from langchain_core.documents import Document
documents = [Document(page_content=raw_document_content, metadata={"source": "manual_input"})]
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
print(f"Split document into {len(texts)} chunks.")

# --- 3. Initialize OpenAI Embeddings ---
try:
    embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    print("OpenAIEmbeddings model initialized.")
except Exception as e:
    print(f"Error initializing OpenAIEmbeddings: {e}")
    exit()

# --- 4. Store Data in Pinecone ---
print(f"Adding {len(texts)} documents to Pinecone index '{index_name}'...")
try:
    vectorstore = PineconeVectorStore.from_documents(
        texts,
        embeddings_model,
        index_name=index_name,
        host=host
    )
    print(f"Successfully added documents to Pinecone index '{index_name}'.")
except Exception as e:
    print(f"Error adding documents to Pinecone: {e}")
    exit()

# --- 5. Perform a Similarity Search ---
query = "What is a vector database used for?"
print(f"\nPerforming similarity search for query: '{query}'")
try:
    docs_found = vectorstore.similarity_search(query)
    print("\n--- Search Results ---")
    if docs_found:
        for i, doc in enumerate(docs_found):
            print(f"Result {i+1}:")
            print(f"  Content: {doc.page_content[:150]}...")
            print(f"  Metadata: {doc.metadata}")
            print("-" * 20)
    else:
        print("No relevant documents found.")
except Exception as e:
    print(f"Error during similarity search: {e}")

print("\nData storage and search demonstration complete.")
print(f"You can now visit your Pinecone console to see the '{index_name}' index.")