from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text_into_chunks(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs = splitter.create_documents([text])
    return [doc.page_content for doc in docs]
