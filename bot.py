import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def start_cmd(update, context):
    update.message.reply_text(f"Hello {update.message.from_user.first_name}.\n\nI can upload photos from telegram to telegra.ph")


def upload_cmd(update, context):
    photo = context.bot.get_file(update.message.photo[-1].file_id)
    photo.download(f'{str(update.message.from_user.id)}.jpg')
    files = {'files': open(f'{str(update.message.from_user.id)}.jpg', 'rb')}
    r = requests.post("https://telegra.ph/upload", files=files)
    info = r.json()
    err = info[0].get("error")
    if err:
        update.message.reply_text(f"Failed to upload. Reason: {err}")
        return
    url = "https://telegra.ph" + info[0].get("src")
    update.message.reply_text(url)
    os.remove(f'{str(update.message.from_user.id)}.jpg')


def upload(update, context):
    size = update.message.document.file_size
    if size > 5242880:
        update.message.reply_text("File size is greater than 5MB")
        return
    photo = context.bot.get_file(update.message.document.file_id)
    mime = update.message.document.file_name[-3:].lower()
    supported = ["jpg", "peg", "png", "gif"]
    if mime not in supported:
        return
    photo.download(f'{str(update.message.from_user.id)}.jpg')
    files = {'files': open(f'{str(update.message.from_user.id)}.jpg', 'rb')}
    r = requests.post("https://telegra.ph/upload", files=files)
    info = r.json()
    err = info[0].get("error")
    if err:
        update.message.reply_text(f"Failed to upload. Reason: {err}")
        return
    url = "https://telegra.ph" + info[0].get("src")
    update.message.reply_text(url)
    os.remove(f'{str(update.message.from_user.id)}.jpg')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    updater = Updater(token=os.environ.get("BOT_TOKEN", None), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(MessageHandler(Filters.photo, upload_cmd))
    dp.add_handler(MessageHandler(Filters.document, upload))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
