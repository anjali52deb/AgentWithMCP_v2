import time
import csv
import os
from datetime import datetime

import sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from agentic_rag.retrieve_router import retrieve_answer

# Simulated query list for testing
QUERIES = [
    "What is our HR policy on sick leave?",
    "What’s the latest transaction history for Q1?"
]

CHUNK_SIZES = [300, 500, 800]
EMBEDDING_MODELS = ["text-embedding-3-small", "text-embedding-ada-002"]  # Expandable

CSV_FILE = r"_Data\rag_quality_results.csv"



def log_result(test_case, query, model, chunk_size, results_found, answer, elapsed):
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.utcnow().isoformat(),
            test_case,
            query,
            model,
            chunk_size,
            results_found,
            int(elapsed * 1000),
            answer[:150].replace("\n", " ") if answer else ""
        ])


def test_chunk_sizes():
    query = input("Enter test query: ")
    model = EMBEDDING_MODELS[0]
    for size in CHUNK_SIZES:
        print(f"\n🧪 Testing chunk size: {size}...")
        start = time.time()
        answer = retrieve_answer(query)
        elapsed = time.time() - start
        log_result("chunk_size_test", query, model, size, answer.count("\n\n"), answer, elapsed)
        print(f"✅ {size} tokens → {answer.count('\\n\\n')} results in {elapsed:.2f}s")


def test_embedding_models():
    query = input("Enter test query: ")
    for model in EMBEDDING_MODELS:
        print(f"\n🧪 Testing embedding model: {model}...")
        start = time.time()
        answer = retrieve_answer(query)
        elapsed = time.time() - start
        log_result("embedding_model_test", query, model, "default", answer.count("\n\n"), answer, elapsed)
        print(f"✅ {model} → {answer.count('\\n\\n')} results in {elapsed:.2f}s")


def batch_store_retrieve():
    for query in QUERIES:
        print(f"\n🧪 Running full RAG test for: {query}")
        start = time.time()
        answer = retrieve_answer(query)
        elapsed = time.time() - start
        log_result("batch_test", query, EMBEDDING_MODELS[0], "default", answer.count("\n\n"), answer, elapsed)
        print(f"✅ {query[:40]}... → {answer.count('\\n\\n')} results in {elapsed:.2f}s")


def export_csv():
    print(f"\n📄 All results are in → {os.path.abspath(CSV_FILE)}")


def main():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp", "test_case", "query", "embedding_model", "chunk_size",
                "results_found", "execution_time_ms", "answer_preview"
            ])

    while True:
        print("""
RAG QUALITY TESTER MENU:
1. Single Query → Test Multiple Chunk Sizes
2. Single Query → Test Multiple Embedding Models
3. Batch Queries → Full RAG pipeline (STORE + RETRIEVE)
4. Export All Results to CSV
0. Exit
""")
        choice = input("Select an option: ")
        if choice == "1":
            test_chunk_sizes()
        elif choice == "2":
            test_embedding_models()
        elif choice == "3":
            batch_store_retrieve()
        elif choice == "4":
            export_csv()
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
