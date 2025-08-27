import google.generativeai as genai
import chromadb
from .config import GEMINI_API_KEY, CHROMA_DB_PATH, COLLECTION_NAME, N_RESULTS_FOR_RAG

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Setup for Chat Model
generation_model = genai.GenerativeModel('gemini-pro')

# Setup for Vector DB Client
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

def get_relevant_documents(question: str) -> list[str]:
    """
    Embeds a user's question and retrieves relevant documents from ChromaDB.
    """
    question_embedding = genai.embed_content(
        model="models/embedding-001",
        content=question,
        task_type="retrieval_query"
    )["embedding"]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=N_RESULTS_FOR_RAG
    )
    return results['documents'][0]

def make_rag_prompt(question: str, relevant_passages: list[str], language_code: str) -> str:
    """
    Creates a prompt for the Gemini model, including context from relevant documents
    and an instruction to reply in a specific language.
    """
    language_map = {
        'ru': 'Russian', 'uz': 'Uzbek', 'en': 'English'
    }
    language_name = language_map.get(language_code, 'the user\'s language')

    escaped_passages = [passage.replace("'", "").replace('"', "").replace("\n", " ") for passage in relevant_passages]
    formatted_passages = "\n- ".join(escaped_passages)
    
    prompt = (f"You are a helpful IT support bot. Answer the user's QUESTION based ONLY on the PROVIDED INFORMATION. "
              f"If the information doesn't contain the answer, say you don't have information on that topic. "
              f"VERY IMPORTANT: You MUST write your entire response in {language_name}.\n\n"
              "PROVIDED INFORMATION:\n"
              f"- {formatted_passages}\n\n"
              "QUESTION:\n"
              f"'{question}'")
    return prompt

def generate_response(prompt: str) -> str:
    """
    Sends the final prompt to the Gemini model and returns the text response.
    """
    response = generation_model.generate_content(prompt)
    return response.text