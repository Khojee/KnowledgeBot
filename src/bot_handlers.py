import logging
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from langdetect import detect, LangDetectException

from . import rag_core
from . import database

# --- Chat History Management ---
MAX_HISTORY_TURNS = 5 # Keep the last 5 Q&A pairs

def get_contextual_history(chat_id: int) -> list:
    """Gets and trims the history to a manageable size for context."""
    history = database.get_chat_history(chat_id)
    # Keep the last MAX_HISTORY_TURNS * 2 messages (user + bot)
    return history[-(MAX_HISTORY_TURNS * 2):]

# --- Telegram Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Hello! I am an AI support bot. How can I help you today?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles messages by first classifying intent, then routing to the appropriate logic.
    """
    user_message = update.message.text
    chat_id = update.message.chat_id
    logging.info(f"Received message from chat_id {chat_id}: {user_message}")

    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    intent = rag_core.classify_intent(user_message)
    response_text = ""
    history = get_contextual_history(chat_id)

    try:
        if intent == 'Greeting':
            response_text = "Hello! How can I help you with our internal applications today?"
        
        elif intent == 'Gratitude':
            response_text = "You're welcome! Is there anything else I can help you with?"

        elif intent == 'Question':
            # This is our original RAG logic
            logging.info("Intent is 'Question'. Running RAG pipeline...")
            detected_lang = 'en'
            try:
                detected_lang = detect(user_message)
            except LangDetectException:
                pass # Default to English
            
            relevant_docs = rag_core.get_relevant_documents(user_message)
            response_text = rag_core.generate_response(
                question=user_message,
                relevant_docs=relevant_docs,
                history=history,
                lang_code=detected_lang
            )
        
        else:
            # Fallback for any other classification
            response_text = "I'm not sure how to respond to that. Can you please ask me a question about our IT systems?"

        # --- Standard response logic (sending message, buttons, saving history) ---
        interaction_id = str(uuid.uuid4())
        keyboard = [
            [
                InlineKeyboardButton("👍 Helpful", callback_data=f"vote:up:{interaction_id}"),
                InlineKeyboardButton("👎 Not Helpful", callback_data=f"vote:down:{interaction_id}"),
            ]
        ]
        # Only add buttons if the response was from the RAG pipeline
        reply_markup = InlineKeyboardMarkup(keyboard) if intent == 'Question' else None

        database.log_interaction(interaction_id, chat_id, user_message, response_text)
        await update.message.reply_text(response_text, reply_markup=reply_markup)
        
        history.append({'role': 'user', 'parts': [user_message]})
        history.append({'role': 'model', 'parts': [response_text]})
        database.save_chat_history(chat_id, history)

    except Exception as e:
        logging.error(f"An error occurred in handle_message: {e}", exc_info=True)
        await update.message.reply_text("Sorry, I encountered an internal error. Please try again.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the vote in the database."""
    query = update.callback_query
    await query.answer("Thank you for your feedback!")

    action, vote, interaction_id = query.data.split(":")

    if action == "vote":
        database.update_vote(interaction_id, vote)
        # Edit the message to remove the buttons after voting for a clean UI
        await query.edit_message_reply_markup(reply_markup=None)