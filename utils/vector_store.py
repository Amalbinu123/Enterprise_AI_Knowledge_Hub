import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.document_loader import load_document

CHROMA_DIR = "chroma_db"

def get_embedding_model():
    """
    Initializes the Google Generative AI embeddings model.
    """
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

def get_vector_store():
    """
    Retrieves or initializes the persistent Chroma vector store.
    """
    embeddings = get_embedding_model()
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

def add_document_to_store(file_path: str):
    """
    Loads, chunks, and adds a document to the persistent ChromaDB.
    Normalizes metadata so we can track and delete it later by its filename.
    """
    db = get_vector_store()
    
    # Load documents using generic loader
    documents = load_document(file_path)
    if not documents:
        return 0
        
    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)
    
    # Normalize source metadata to just the filename
    filename = os.path.basename(file_path)
    for chunk in chunks:
        chunk.metadata["source"] = filename
        if "page" not in chunk.metadata:
            chunk.metadata["page"] = 0  # default page number if missing
            
    # Add documents to ChromaDB
    db.add_documents(chunks)
    return len(chunks)

def delete_document_from_store(filename: str):
    """
    Deletes all vector store entries corresponding to the source filename.
    """
    db = get_vector_store()
    db.delete(where={"source": filename})