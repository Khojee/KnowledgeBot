import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("API keys for Telegram and Gemini must be set in the .env file.")

# Vector DB Configuration
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "bank_it_support"

# Knowledge Base
KNOWLEDGE_BASE_DIR = "knowledge_base"

# RAG Configuration
N_RESULTS_FOR_RAG = 3 # Number of documents to retrieve for context