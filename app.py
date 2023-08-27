# Added modules
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Application modules
from handlers.handlers import *
from config import TOKEN

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)


def application():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    app = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # on non command i.e. message - echo the message on Telegram
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))
    # Add a handler for photo messages
    app.add_handler(MessageHandler(filters.PHOTO, echo_photo))

    # ...and the error handler
    app.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES)
