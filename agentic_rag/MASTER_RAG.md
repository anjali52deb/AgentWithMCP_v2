✅ Got it — here's a detailed and structured **README for the Master RAG Agent** that captures exactly what we've built so far. This will let you pause, study LangGraph, and resume smoothly when you're ready.

---

# 🧠 Master RAG Agent (`MasterRAGAgent`)

This component is the centralized **decision engine** for your Agentic RAG system. It intelligently decides whether to run a **STORE** or **RETRIEVE** workflow based on the input, and it encapsulates both logic flows with modular, extensible design.

---

## 📂 Location: `rag_controller.py`

> Defines a single unified class: `MasterRAGAgent`

---

## ✅ Capabilities

| Mode          | Description                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------- |
| 🧠 `auto`     | Automatically detects whether to store or retrieve based on inputs                                |
| 📥 `store`    | Takes a file path, chunks content, embeds it, and stores it in the appropriate MongoDB index      |
| 🔍 `retrieve` | Accepts a query, classifies subject, retrieves relevant chunks, and synthesizes an answer via LLM |

---

## 🧩 How it Decides What to Do

You can simply call:

```python
agent.run(query="...", file=None)     → RETRIEVE mode
agent.run(file="some.pdf", query=None) → STORE mode
agent.run(query="...", mode="retrieve") → Force retrieve
agent.run(file="...", mode="store")     → Force store
```

---

## 🔁 Flow (Aligned with Diagram)

```
User Input
   ↓
[ MasterRAGAgent.run(...) ]
   ↓
[ RAG Mode Selector ]
   ↓
Store Path or Retrieve Path

STORE:
→ load_file()
→ classify_subject()
→ embed_and_store()

RETRIEVE:
→ detect_subject_from_query()
→ get_retriever_model()
→ retriever.invoke(query)
→ synthesize_with_llm()
→ evaluate_retrieve_quality()
→ log_retrieve_event()
→ clean_logs_once_per_day()
```

---

## 🔧 Dependencies and Assumptions

| Component               | Source                   | Notes                        |
| ----------------------- | ------------------------ | ---------------------------- |
| `load_file()`           | `attachment_handlers.py` | Loads and chunks files       |
| `embed_and_store()`     | `embedding_factory.py`   | Embeds and writes to MongoDB |
| `get_retriever_model()` | `retriever_factory.py`   | Embedding-aware retriever    |
| `log_utils`             | `log_utils.py`           | Logging + daily cleanup      |
| `mongo_config.json`     |                          | Subject-to-index mapping     |

---

## 🧪 Retrieval Quality Evaluation

Currently:

* Logs how many chunks were retrieved
* Shows chunk previews for debug

Future (planned):

* Avg score
* Match percentage above threshold
* Subject hit rate

---

## 🧠 Subject Detection (for queries)

Basic keyword matching:

* `"profile"` → profile DB
* `"history"` → history DB
* `"mongodb"`, `"index"` → default
* Default fallback if no match

---

## 🚧 To Be Done (Future Work)

| Feature                         | Purpose                                                  |
| ------------------------------- | -------------------------------------------------------- |
| Implement LangGraph wrapper     | Turn this into async, stateful LangChain node graph      |
| Add persistent log cleanup      | Right now cleanup flag resets per process                |
| Add advanced subject classifier | Use LLM or TF-IDF to auto-classify subject on query/file |
| Add UI/API interface            | Trigger via FastAPI or Streamlit instead of script       |
| Add chunk score metrics         | For retrieval quality tracking                           |

---

## ✅ How to Use (Python)

```python
from rag_controller import MasterRAGAgent

agent = MasterRAGAgent(embedding_provider=\"gpt\")

# Retrieve mode
response = agent.run(query=\"What is the MongoDB index update?\")
print(response)

# Store mode
agent.run(file=\"docs/faq.pdf\")
```

---

Let me know if you'd like me to save this into a `README_Agent.md` file or generate a markdown download. You're in a solid place to resume from here.
