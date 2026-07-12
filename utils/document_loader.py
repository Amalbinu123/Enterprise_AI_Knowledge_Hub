import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def load_document(file_path: str):
    """
    Loads and parses a document based on its file extension.
    Supports: PDF, DOCX, TXT, MD, HTML
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        return loader.load()
    elif ext == ".docx":
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(file_path)
        return loader.load()
    elif ext in [".txt", ".md"]:
        loader = TextLoader(file_path, encoding="utf-8")
        return loader.load()
    elif ext in [".html", ".htm"]:
        from langchain_community.document_loaders import BSHTMLLoader
        loader = BSHTMLLoader(file_path)
        return loader.load()
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
