import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.config import TELEGRAM_BOT_TOKEN
from src.bot_handlers import start, handle_message
from src.utils import setup_logging

def main() -> None:
    """Start the bot."""
    # Set up logging
    setup_logging()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    logging.info("Multilingual Support Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()