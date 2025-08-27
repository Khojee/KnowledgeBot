import logging
from telegram import Update
from telegram.ext import ContextTypes
from langdetect import detect, LangDetectException
from . import rag_core

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Hello! I am an AI support bot. How can I help you today?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text messages and uses the RAG core to generate a response."""
    user_message = update.message.text
    chat_id = update.message.chat_id
    
    logging.info(f"Received message from chat_id {chat_id}: {user_message}")

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')

        try:
            detected_lang = detect(user_message)
        except LangDetectException:
            detected_lang = 'en' # Default to English if detection fails
        
        # 1. Retrieve relevant documents
        relevant_docs = rag_core.get_relevant_documents(user_message)
        
        # 2. Create the prompt
        prompt = rag_core.make_rag_prompt(user_message, relevant_docs, detected_lang)
        
        # 3. Generate the response
        response_text = rag_core.generate_response(prompt)
        
        # 4. Send the response to the user
        await update.message.reply_text(response_text)

    except Exception as e:
        logging.error(f"An error occurred in handle_message: {e}", exc_info=True)
        await update.message.reply_text("Sorry, I encountered an error. Please try again.")