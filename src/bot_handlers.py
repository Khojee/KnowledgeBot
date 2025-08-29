import logging
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from langdetect import detect, LangDetectException

from . import rag_core
from . import database

# --- Chat History Management ---
MAX_HISTORY_TURNS = 5

# --- Telegram Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Hello! I am an AI support bot. How can I help you today?")

async def handle_group_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /ask command in group chats.
    Ignores history and relies on explicit activation.
    """
    # When a command is used, the user's message is in `context.args`
    if not context.args:
        # If the user just sends "/ask" with no question, guide them.
        await update.message.reply_text("Please ask a question after the /ask command. For example: /ask Submit button ishlamayapti")
        return

    user_message = " ".join(context.args)
    chat_id = update.message.chat_id # This will be the group's ID
    user_id = update.message.from_user.id # We can still log the specific user
    
    logging.info(f"Received /ask command from user {user_id} in group {chat_id}: {user_message}")

    try:
        # We don't need to send "typing" in a busy group chat.
        
        # --- Simplified RAG Pipeline (No History) ---
        detected_lang = 'en'
        try:
            detected_lang = detect(user_message)
        except LangDetectException:
            pass
        
        relevant_docs = rag_core.get_relevant_documents(user_message)
        
        # We call generate_response with an EMPTY history list.
        response_text = rag_core.generate_response(
            question=user_message,
            relevant_docs=relevant_docs,
            history=[], # <-- NO HISTORY
            lang_code=detected_lang
        )

        # --- Voting and Reply Logic ---
        interaction_id = str(uuid.uuid4())
        keyboard = [
            [
                InlineKeyboardButton("👍 Helpful", callback_data=f"vote:up:{interaction_id}"),
                InlineKeyboardButton("👎 Not Helpful", callback_data=f"vote:down:{interaction_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Log the interaction. We can still log the user ID for analytics.
        database.log_interaction(interaction_id, user_id, user_message, response_text)
        
        # IMPORTANT: Use reply_to_message_id to create a threaded reply.
        await context.bot.send_message(
            chat_id=chat_id,
            text=response_text,
            reply_to_message_id=update.message.message_id, # This makes it a reply
            reply_markup=reply_markup
        )

    except Exception as e:
        logging.error(f"An error occurred in handle_group_ask: {e}", exc_info=True)
        # Reply to the user's message to notify them of the error
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