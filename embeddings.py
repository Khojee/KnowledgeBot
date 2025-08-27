import google.generativeai as genai
import chromadb
import os
import logging
from src.config import GEMINI_API_KEY, CHROMA_DB_PATH, COLLECTION_NAME, KNOWLEDGE_BASE_DIR
from src.utils import setup_logging

setup_logging()
genai.configure(api_key=GEMINI_API_KEY)

def process_and_embed_documents():
    """
    Processes text files from the knowledge base, embeds them using Gemini,
    and stores them in ChromaDB.
    """
    logging.info("Starting document processing and embedding...")
    
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    doc_ids = []
    documents = []
    
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
         logging.error(f"Knowledge base directory not found at: {KNOWLEDGE_BASE_DIR}")
         return

    for i, filename in enumerate(os.listdir(KNOWLEDGE_BASE_DIR)):
        if filename.endswith(".txt"):
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                documents.append(f.read())
            doc_ids.append(str(i))

    if not documents:
        logging.warning("No documents found in the knowledge base directory.")
        return

    logging.info(f"Found {len(documents)} documents to embed.")
    
    try:
        embeddings = genai.embed_content(
            model="models/embedding-001",
            content=documents,
            task_type="retrieval_document"
        )["embedding"]

        collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=doc_ids
        )
        logging.info(f"Successfully added {len(documents)} documents to the vector database.")
    except Exception as e:
        logging.error(f"Failed to embed and add documents: {e}")

if __name__ == "__main__":
    process_and_embed_documents()