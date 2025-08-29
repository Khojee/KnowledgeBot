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
    Creates a single, comprehensive prompt for the Gemini model that defines its persona
    and rules for handling questions, greetings, and gratitude.
    """
    language_map = { 'ru': 'Russian', 'uz': 'Uzbek', 'en': 'English' }
    language_name = language_map.get(language_code, 'the user\'s language')

    # --- THE NEW MASTER PROMPT ---
    
    # Rule 1: Define the bot's core persona and primary goal.
    prompt = (f"You are a friendly and helpful IT support bot for a bank. Your primary goal is to answer user questions about internal applications. "
              f"VERY IMPORTANT: You MUST write your entire response in {language_name}.\n\n"
              f"If you can't identify the user's language, respond in Uzbek. If users asks questions in Uzbek but written with Cyrillic characters, respond in Uzbek as well.\n\n"
              "--- RULES ---\n"
              "1. If the user asks a specific question, answer it based ONLY on the PROVIDED INFORMATION below. "
              "2. If the PROVIDED INFORMATION is empty or does not contain the answer to the user's question, you MUST respond with: 'I'm sorry, I don't have information on that topic. Please ask another question or contact the IT department.' "
              "3. If the user's message is a simple greeting (like 'hello', 'hi', 'salom'), respond with a friendly, brief greeting in {language_name}. Do not use the provided information. "
              "4. If the user's message is an expression of gratitude (like 'thank you', 'rahmat'), respond warmly and ask if you can help with anything else, in {language_name}. Do not use the provided information.\n\n"
              "--- PROVIDED INFORMATION ---\n")

    # Rule 2: Add the retrieved documents, or state that none were found.
    if relevant_passages:
        escaped_passages = [passage.replace("'", "").replace('"', "").replace("\n", " ") for passage in relevant_passages]
        formatted_passages = "\n- ".join(escaped_passages)
        prompt += f"- {formatted_passages}\n\n"
    else:
        prompt += "No relevant information was found.\n\n"

    # Rule 3: Add the user's actual message.
    prompt += f"--- USER'S MESSAGE ---\n'{question}'"
              
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
    