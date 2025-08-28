import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler # NEW
from src.config import TELEGRAM_BOT_TOKEN
from src.bot_handlers import start, handle_message, button_handler # NEW: import button_handler
from src.utils import setup_logging
from src.database import init_db # NEW

def main() -> None:
    """Start the bot."""
    setup_logging()
    
    # NEW: Initialize the database when the bot starts
    init_db()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # NEW: Add the handler for button clicks
    application.add_handler(CallbackQueryHandler(button_handler))

    logging.info("Enhanced Bot with history and voting is running...")
    application.run_polling()

if __name__ == '__main__':
    main()