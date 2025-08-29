import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler # MODIFIED: Added CallbackQueryHandler
from src.config import TELEGRAM_BOT_TOKEN
from src.bot_handlers import start, handle_group_ask, button_handler # MODIFIED: handle_message -> handle_group_ask
from src.utils import setup_logging
from src.database import init_db

def main() -> None:
    """Start the bot in Group Chat Mode."""
    setup_logging()
    init_db()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # --- MODIFIED HANDLERS ---
    # The /start command still works in a private chat with the bot
    application.add_handler(CommandHandler("start", start))

    # This is the NEW primary handler. It only triggers on the /ask command.
    application.add_handler(CommandHandler("ask", handle_group_ask))
    
    # The button handler for voting remains the same
    application.add_handler(CallbackQueryHandler(button_handler))

    logging.info("Group Chat Bot is running, listening for /ask commands...")
    application.run_polling()

if __name__ == '__main__':
    main()