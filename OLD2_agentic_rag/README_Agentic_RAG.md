
# 🧠 Agentic-RAG System (Refactored)

This project is an enterprise-grade **Agentic-RAG** system built using LangChain/LangGraph and MongoDB Vector Search. It supports intelligent document storage, retrieval, chunk/embedding quality tests, and full logging with decision-agent routing.

---

## 📦 Project Overview

### 🔁 Two Core Pipelines
- **store_pipeline.py** – Handles file chunking, embedding, deduplication, and vector DB storage
- **retrieve_pipeline.py** – Handles query classification, subject-based routing, retrieval, and fallback logic

### 🤖 AI Agents
- **master_rag_agent.py** – Central decision engine, routes user intent to STORE or RETRIEVE
- **intent_classifier.py** – Classifies query as "RAG-Store" or "RAG-Retrieve"
- **subject_classifier.py** – Determines subject (e.g., HR, Finance) from filename or query

### 🧠 Embedding & VectorDB
- **mongo_client.py** – MongoDB connection and helper
- **vectorstore_manager.py** – Interfaces with MongoDB Atlas Vector Search
- **index_manager.py** – Ensures index creation for new subject collections
- **subject_db_mapper.py** – Maps subject labels to DB and collection names

---

## ✅ Refactored & Consolidated Modules

| New File         | Merged From                                       |
|------------------|----------------------------------------------------|
| `logger.py`      | `store_logger.py`, `retrieve_logger.py`           |
| `llm_engine.py`  | `LLM_LangChain.py`, `llm_wrapper.py`               |
| `file_loader.py` | `attachment_handlers.py`, `universal_loader.py`   |
| `log_reader.py`  | `log_metadata_reader.py`, `log_viewer.py`         |

---

## ⚙️ Configuration Files

| File                    | Purpose                          |
|-------------------------|----------------------------------|
| `db_config.py`          | DB connection and default config |
| `vector_db_config.json` | Subject-to-DB/index mapping      |
| `config.py`             | General constants                |

---

## 📂 Utility Modules

| File                 | Description                        |
|----------------------|------------------------------------|
| `store_index_utils.py` | Utilities for creating indexes   |
| `utils.py`             | Common helpers (hashing, parsing)|
| `index_router.py`      | Optional future use              |

---

## 🧪 Testing & Logging

- All STORE and RETRIEVE flows are logged into MongoDB.
- Use `log_reader.py` to inspect logs.
- Use `test_code/Test_all_agentic_rag.py` for unified CLI testing.

---

## 🚀 Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your `.env` with MongoDB URI and OpenAI keys.

3. Run the unified test script:
   ```bash
   python test_code/Test_all_agentic_rag.py
   ```

---

## 🧼 Cleanup Checklist

If validated:
- ❌ Delete: `store_logger.py`, `retrieve_logger.py`
- ❌ Delete: `LLM_LangChain.py`, `llm_wrapper.py`
- ❌ Delete: `attachment_handlers.py`, `universal_loader.py`
- ❌ Delete: `log_metadata_reader.py`, `log_viewer.py`

---

## 📈 What's Next?

- LangGraph migration for async and event-based control
- LangSmith integration for traces and observability
- Semantic scoring and RAG Quality visual dashboard

---
