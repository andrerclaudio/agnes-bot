# pylint: disable=missing-module-docstring missing-function-docstring wrong-import-order unused-argument import-error useless-return
# pylint: disable=line-too-long too-many-locals invalid-name unused-import consider-using-f-string wildcard-import unused-wildcard-import

# Build-in modules
import logging
import os

# Added modules
import numpy as np
from PIL import Image
from telegram import ForceReply, Update, InputFile
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import requests

# Application modules
from board.raspberry import DigitalFinger
from config import CHAT_ID, AUTH_USER, TOKEN
from intelligence.pallet import dominant_colors

# Logging handler
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Send me a picture and I will return \
                                     the dominant colors on it!")


async def echo_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def colors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the user the dominant colors."""

    # Get the largest available photo
    photo = update.message.photo[-1]
    file_id = photo.file_id

    # Download the photo
    photo_file = await context.bot.get_file(file_id)
    await photo_file.download_to_drive("{}.jpg".format(file_id))
    photo_path = "{}.jpg".format(file_id)

    # Get the dominant colors using the provided dominant_colors function
    dmt = dominant_colors(photo_path, calculate_optimal=False)

    # Ensure RGB values are within 0-255 range
    valid_colors = [(r, g, b) for r, g, b in dmt if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255]

    if len(valid_colors) == 0:
        await update.message.reply_text("No valid dominant colors found.")
        return

    # Open the image
    img = Image.open(photo_path)
    img_array = np.array(img)

    # Calculate the width of each color slice
    slice_width = img.width // len(valid_colors)

    # Create a new image array with each slice representing a dominant color
    new_img_array = np.zeros_like(img_array)
    for i, (r, g, b) in enumerate(valid_colors):
        color_array = np.array([r, g, b])
        slice_mask = np.zeros_like(img_array[:, :, 0], dtype=bool)
        slice_mask[:, i * slice_width: (i + 1) * slice_width] = True
        new_img_array[slice_mask] = color_array

    # Create a new image from the new array
    new_img = Image.fromarray(new_img_array.astype(np.uint8))

    # Save the new image
    new_photo_path = "{}_color_slices.jpg".format(file_id)
    new_img.save(new_photo_path, quality=95)

    # Reply with the new image
    with open(new_photo_path, 'rb') as photo_stream:
        await update.message.reply_photo(photo=InputFile(photo_stream))

    # Clean up files
    os.remove(photo_path)
    os.remove(new_photo_path)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""

    logger.error("Exception while handling an update:", exc_info=False)
    message = (
        f"An exception was raised while handling an update\n"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


async def asimov_control(update: Update, finger: DigitalFinger) -> None:
    """Turn on and off Asimov remote server."""

    # Check if the user ID from the incoming update matches the one you want to filter
    if str(update.message.from_user.id) == str(AUTH_USER):

        # Call the method to turn on the server
        if finger.digital_finger():
            await update.message.reply_text("Server turned on/off successfully!")
        else:
            await update.message.reply_text("Failed to turn on/off the server.")

    else:
        await update.message.reply_text("You are not authorized to use this bot.")


def send_telegram_message(message) -> None:
    """
    Sends a text message to a Telegram chat using the Telegram Bot API.

    Parameters:
    - message (str): The text message to be sent.

    Returns:
    None

    Note:
    Ensure that the `TOKEN` and `CHAT_ID` variables are properly configured with the
    Telegram Bot API token and the target chat ID before using this function.

    Example:
    ```
    send_telegram_message("Hello, world!")
    ```
    """

    send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + CHAT_ID + '&parse_mode=Markdown&text=' + message

    try:
        # Send the message to the specified chat ID
        response = requests.get(send_text)
        logging.debug(response)

    except requests.exceptions as e:
        logging.error(f"Error sending message to Telegram: {str(e)}", exc_info=False)