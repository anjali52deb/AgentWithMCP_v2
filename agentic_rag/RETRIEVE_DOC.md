Here is your detailed, up-to-date **`README.md` for the RETRIEVE pipeline** — covering architecture, logic, design choices, error handling, and extensibility.

---

# 🧠 Agentic RAG: RETRIEVE Pipeline (Modular)

## ✅ Overview

The RETRIEVE pipeline is part of a modular Agentic RAG system that retrieves relevant context chunks from a MongoDB Atlas Vector Store and synthesizes LLM-based answers. It supports both **GPT** and **Gemini** embeddings, and uses subject-specific routing, logging, and intelligent fallback mechanisms.

---

## 🗂️ Key Files & Responsibilities

| File                   | Purpose                                                               |
| ---------------------- | --------------------------------------------------------------------- |
| `retrieve_pipeline.py` | Main entrypoint for retrieving context & answering queries            |
| `retriever_factory.py` | Constructs subject-aware retrievers using embedding provider & config |
| `mongo_config.json`    | Routing + index config per subject (`profile`, `history`, `default`)  |
| `mongo_utils.py`       | Loads config and connects to MongoDB                                  |
| `log_utils.py`         | Logs RETRIEVE calls, purges old logs, throttles cleanup to once/day   |

---

## 🔄 End-to-End Flow

```text
User Query
   │
   ▼
[detect_subject_from_query()] → subject (e.g., 'profile')
   │
   ▼
[get_retriever_model(subject, provider)] → builds retriever using subject-specific index
   │
   ▼
[retriever.invoke(query)] → retrieves top-K matching chunks
   │
   ▼
[synthesize_with_llm()] → generates final answer using GPT-4
   │
   ▼
[log_retrieve_action()] → stores log, triggers once-per-day cleanup
```

---

## ⚙️ Intelligent Components

### 🔍 Subject Detection

* Based on keywords (`profile`, `history`, `index`, etc.)
* Falls back to `"default"` if no match

### 📚 Retriever Factory

* Dynamically selects:

  * `collection_name`
  * `index_name`
  * `embedding provider`
* Uses `text_key="chunk_text"` for MongoDB Atlas
* Handles embedding mismatch errors gracefully

### 🧼 Logging & Cleanup

* Logs every RETRIEVE event with query, subject, match count
* Daily cleanup runs **only once per day**
* Controlled via in-memory `_last_cleanup_date`

---

## 🧪 Error Handling

| Scenario                     | Behavior                                                     |
| ---------------------------- | ------------------------------------------------------------ |
| Embedding dimension mismatch | Detects vector size error and raises a friendly RuntimeError |
| Invalid subject              | Falls back to `default` if available, else raises ValueError |
| Zero matches                 | Returns graceful fallback from prompt synthesis              |
| MongoDB unreachable          | Raises connection error as-is (fail-fast)                    |

---

## ⚠️ Warnings/Deprecations

* `.get_relevant_documents()` was replaced with `.invoke()` to support LangChain >= v0.1.46
* `OpenAIEmbeddings` is deprecated in older import paths — now using `langchain_openai`

---

## 📁 Config Format (`mongo_config.json`)

```json
"profile": {
  "db_name": "agentic_rag",
  "collection_name": "Profile_DB",
  "index_name": "vector_index_profile_db",
  "top_k": 3
},
"default": {
  "collection_name": "Misc_DB",
  "index_name": "vector_index_misc_db"
}
```

Add separate `index_name_gpt` and `index_name_gemini` if using dual-index architecture.

---

## 🧰 How to Extend

| Task                              | Approach                                                                         |
| --------------------------------- | -------------------------------------------------------------------------------- |
| Add new subject (e.g. "projects") | Add config block in `mongo_config.json` and extend `detect_subject_from_query()` |
| Support more embedding providers  | Add logic in `retriever_factory.py`                                              |
| Persist log cleanup state         | Save `_last_cleanup_date` to file/DB instead of memory                           |
| Add quality testing               | Create `retrieve_quality_tester.py` to track match scores & chunk diversity      |

---

## ✅ Ready to Use

You can now:

* Call `retrieve_answer(query, subject_hint=None)` from anywhere
* Switch embedding providers by setting: `EMBEDDING_PROVIDER=gpt` or `gemini`
* Monitor logs in MongoDB (`agentic_rag_logs.retrieve_logs`)
* Run tests using `Test_RETRIEVE_with_Embedding_Switch.py`

---

Let me know if you want this saved as a `README.md` file or added to a documentation page.
