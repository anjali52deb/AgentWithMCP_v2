# attachment_handlers.py
# universal_loader.py

"""
Loads different file formats for RAG Store pipeline:
Supports: PDF, TXT, JSON, HTML (basic)
Returns: List[Document] objects
"""


import os
import whisper
import docx2txt
from langchain_community.document_loaders import PyPDFLoader, TextLoader, JSONLoader, UnstructuredHTMLLoader
from langchain.schema import Document


def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        return _combine_docs(docs)

    elif ext == ".txt":
        loader = TextLoader(file_path)
        docs = loader.load()
        return _combine_docs(docs)

    elif ext == ".json":
        loader = JSONLoader(file_path)
        docs = loader.load()
        return _combine_docs(docs)

    elif ext == ".html":
        loader = UnstructuredHTMLLoader(file_path)
        docs = loader.load()
        return _combine_docs(docs)

    elif ext == ".docx":
        text = docx2txt.process(file_path)
        return text.strip()

    elif ext == ".srt":
        return _parse_srt(file_path)

    # elif ext == ".mp4":
    #     return _transcribe_audio(file_path)

    else:
        raise ValueError(f"❌ Unsupported file format: {ext}")


def _combine_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def _transcribe_audio(file_path: str) -> str:
    model = whisper.load_model("base")  # or "medium" if size allows
    result = model.transcribe(file_path)
    return result["text"].strip()


def _parse_srt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    text_lines = []
    for line in lines:
        line = line.strip()
        if line.isdigit() or "-->" in line or line == "":
            continue
        text_lines.append(line)

    return " ".join(text_lines)




def load_file(filepath: str) -> list[Document]:
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return PyPDFLoader(filepath).load()

    elif ext == ".txt":
        return TextLoader(filepath).load()

    elif ext == ".json":
        return JSONLoader(filepath).load()

    elif ext == ".html":
        return UnstructuredHTMLLoader(filepath).load()

    else:
        raise ValueError(f"❌ Unsupported file format: {ext}")
