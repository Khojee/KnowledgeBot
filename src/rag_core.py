import google.generativeai as genai
import chromadb
from .config import GEMINI_API_KEY, CHROMA_DB_PATH, COLLECTION_NAME, N_RESULTS_FOR_RAG
import logging

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Setup for Chat Model
# Using a specific, stable model version is a good practice.
generation_model = genai.GenerativeModel('gemini-2.5-flash')

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
    language_map = { 'ru': 'Russian', 'uz': 'Uzbek', 'en': 'English' }
    language_name = language_map.get(language_code, 'the user\'s language')
    escaped_passages = [passage.replace("'", "").replace('"', "").replace("\n", " ") for passage in relevant_passages]
    formatted_passages = "\n- ".join(escaped_passages)
    
    prompt = (f"You are a helpful IT support bot. Based ONLY on the PROVIDED INFORMATION, answer the user's QUESTION. "
              f"If the information doesn't contain the answer, say you don't have information on that topic. And ask the user for clarification."
              f"If the user greets you, respond with a friendly greeting."
              f"If the user expresses gratitude, acknowledge it warmly."
              f"VERY IMPORTANT: You MUST write your entire response in {language_name}.\n\n"
              "PROVIDED INFORMATION:\n"
              f"- {formatted_passages}\n\n"
              "QUESTION:\n"
              f"'{question}'")
    return prompt


def generate_response(question: str, relevant_docs: list, history: list, lang_code: str) -> str:
    """
    Generates a response using RAG context and conversational history.
    Includes safety checks to prevent crashes on empty responses.
    """
    chat_session = generation_model.start_chat(history=history)
    prompt_for_this_turn = make_rag_prompt(question, relevant_docs, lang_code)
    
    try:
        response = chat_session.send_message(prompt_for_this_turn)
        if response.candidates and response.candidates[0].content.parts:
            return response.text
        else:
            # If the response is empty due to safety or other reasons, return a polite default.
            logging.warning("Gemini returned an empty response, likely due to safety filters.")
            return "I'm sorry, I'm not able to respond to that."
    except Exception as e:
        logging.error(f"Error during Gemini API call: {e}")
        return "I encountered an issue trying to generate a response."
    
def classify_intent(question: str) -> str:
    """Uses Gemini to classify the user's intent."""
    prompt = f"""
    Classify the user's message into one of the following categories:
    'Question', 'Greeting', 'Gratitude'.
    Message: "{question}"
    Category:
    """
    try:
        # Use the generate_content function for simple, non-chat requests
        response = generation_model.generate_content(prompt)
        # Clean up the response to get just the category word
        intent = response.text.strip().replace("'", "").replace('"', '')
        logging.info(f"Classified intent as: {intent}")
        if intent in ['Question', 'Greeting', 'Gratitude']:
            return intent
        else:
            # If the model gives a weird response, default to a question
            return 'Question'
    except Exception as e:
        logging.error(f"Could not classify intent: {e}")
        return 'Question'