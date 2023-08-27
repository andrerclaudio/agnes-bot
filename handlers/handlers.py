# Build-in modules
import html
import json
import traceback
import logging
import os

# Added modules
from telegram import ForceReply, Update, InputFile
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import numpy as np
from PIL import Image, ImageDraw

# Application modules
from config import CHAT_ID
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
    await update.message.reply_text("Help!")


async def echo_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def echo_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the received photo back to the user with dominant colors."""

    # Get the largest available photo
    photo = update.message.photo[-1]
    file_id = photo.file_id

    # Download the photo
    photo_file = await context.bot.get_file(file_id)
    await photo_file.download_to_drive("{}.jpg".format(file_id))
    photo_path = "{}.jpg".format(file_id)

    # Get the dominant colors using the provided dominant_colors function
    colors = dominant_colors(photo_path)

    # Ensure RGB values are within 0-255 range
    valid_colors = [(r, g, b) for r, g, b in colors if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255]

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
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096-character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )
