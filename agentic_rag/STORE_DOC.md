Great — here is a **developer-friendly documentation** for your Agentic-RAG **STORE + STORE LOG + Embedding Switch** flow. This reflects your latest code, explains the purpose of each module, and guides future maintainers.

---

# 🧾 Agentic-RAG: STORE + LOGGING + Embedding Provider Switch (GPT/Gemini)

## 🔄 Overview

The **`store_pipeline.py`** module implements the STORE phase of your Agentic-RAG system. It:

* Loads various file formats (PDF, DOCX, TXT, CSV, XLSX, JSON, HTML)
* Chunks + embeds content using either **OpenAI (GPT)** or **Google Gemini**
* Stores vectors into a MongoDB vector collection based on subject type
* Logs metadata into a separate logging database
* Supports full traceability, environment-based switches, and debugging

---

## 📁 Core Components

### 1. `store_pipeline.py` — Main Driver

#### 🔧 Setup

```python
from agentic_rag.embedding_factory import get_embedding_model
from agentic_rag.gemini_embedder import GeminiEmbeddings
```

* Loads config from `mongo_config.json`
* Auto-detects file subject from name (`profile_`, `history_`, etc.)
* Configures chunk size & overlap per subject
* Embeds using either GPT or Gemini (via `.env` or CLI switch)

---

## 🧠 Embedding Provider Switch (GPT / Gemini)

### 🔀 Switch with `.env` or CLI

```env
EMBEDDING_PROVIDER=gpt  # or gemini
```

```bash
python Test_STORE_with_Embedding_Switch.py gemini
```

### `embedding_factory.py`

```python
def get_embedding_model(provider: str):
    if provider == EmbeddingProvider.OPENAI:
        return OpenAIEmbeddings()
    elif provider == EmbeddingProvider.GEMINI:
        return GeminiEmbeddings()
```

### `gemini_embedder.py`

Uses Google Gemini's `embed_content()` API:

```python
genai.embed_content(
    model=self.model.name,
    content=text,
    task_type="retrieval_document"
)
```

---

## 📦 MongoDB Routing

### `mongo_config.json`

Subject-based routing with custom chunk settings:

```json
"profile": {
  "collection_name": "Profile_DB",
  "chunk_size": 700,
  "chunk_overlap": 150
},
"history": {
  "collection_name": "History_DB",
  "chunk_size": 600,
  "chunk_overlap": 120
}
```

Uses `routing_keywords` to match filename prefixes like `profile_`, `emp_`.

---

## 🧩 Pipeline Stages

### ✅ Step 1: Input & Config Load

```python
load_config()  # reads JSON config
extract_file_metadata()  # hashes, sizes, user_id, timestamps
```

### ✅ Step 2: Duplicate Check

```python
is_duplicate_upload()  # prevents re-insertion
```

### ✅ Step 3: Subject Detection

```python
detect_subject_from_filename()  # uses prefix-based tagging
```

### ✅ Step 4: Text Extraction & Chunking

```python
extract_text_from_file()  # handles PDF, DOCX, TXT, CSV, XLSX, HTML
chunk_text()  # with overlap
```

### ✅ Step 5: Embedding

```python
embedding_fn = embed_documents() or embed_query()
embed_chunks()  # hashes each chunk and logs char count
```

### ✅ Step 6: STORE + LOG

```python
store_vectors_to_db()
log_store_metadata()
```

---

## 🗂️ STORE Vector Schema

Each MongoDB vector document includes:

```json
{
  "chunk_text": "...",
  "embedding": [...],
  "subject": "profile",
  "file_hash": "...",
  "upload_time": "...",
  "store_pipeline_version": "v1.0",
  "metadata": {
    "chunk_hash": "...",
    "char_count": 420
  }
}
```

---

## 📝 Log Metadata Format

Stored in:

```json
agentic_rag_logs.store_logs
```

Includes:

* `file_name`, `user_id`, `upload_time`
* `subject`, `chunk_count`, `chunk_size`, `chunk_overlap`
* `embedding_model` (gpt or gemini)
* `store_pipeline_version`

---

## 🧪 How to Test

```bash
# Test with Gemini embeddings
python Test_STORE_with_Embedding_Switch.py gemini

# Test with GPT (OpenAI) embeddings
python Test_STORE_with_Embedding_Switch.py gpt
```

---

## ✅ Final Notes

* `STORE_PIPELINE_VERSION` is configurable in `.env`
* Logging supports file-based logging via `LOG_TO_FILE=true`
* Dynamic fallback and default routes ensure robustness

---

Would you like this documentation exported as a `.md` or `.docx` file for your project folder?
