# pylint: disable=missing-module-docstring missing-function-docstring wrong-import-order unused-argument import-error useless-return
# pylint: disable=line-too-long too-many-locals invalid-name unused-import consider-using-f-string wildcard-import unused-wildcard-import

# Build-in modules
import time

# Added modules
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Application modules
from config import TOKEN
from handlers.handlers import *
from mqtt.mqtt import AgnesMqttClient

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)


def application():
    # The application start from here
    logging.info('The application has started!')

    # Just a delay doing nothing and making sure the connection was properly established.
    time.sleep(60)

    """Init the class to control the raspberry pi PIN."""
    finger = DigitalFinger()

    """Init the Mqtt class."""
    BROKER_ADDRESS = "mqtt.eclipseprojects.io"
    PORT = 1883
    client = AgnesMqttClient() 

    try:

        """Start Mqtt client."""
        client.mqttc.connect(BROKER_ADDRESS, PORT)
        client.mqttc.loop_start()

        """Start the bot."""
        # Create the Application and pass it your bot's token.
        bot = Application.builder().token(TOKEN).build()

        # on different commands - answer in Telegram
        bot.add_handler(CommandHandler("start", start))
        bot.add_handler(CommandHandler("help", help_command))
    
        # Add the new "Asimov" command handler
        bot.add_handler(CommandHandler("Asimov", lambda update, context: asimov_control(update, finger)))
    
        # on non command i.e. message - echo the message on Telegram
        bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text))
        # Add a handler for photo messages
        bot.add_handler(MessageHandler(filters.PHOTO, colors))
    
        # ...and the error handler
        bot.add_error_handler(error_handler)
    
        # Run the bot until the user presses Ctrl-C
        bot.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logging.error(f"Something went wrong -- {str(e)}", exc_info=False) 

    finally:
        # Clean up GPIO and exit
        finger.clean()
        client.mqttc.disconnect()
        logging.info("Disconnected from MQTT broker, Telegram Bot and Reset PIN settings.")
