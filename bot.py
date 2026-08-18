import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from deep_translator import GoogleTranslator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalawma aleykum! Men qaraqalpaqsha awdarma botpan.\n\n"
        "Maga qanday tildegi tekst jiberseniz, ozbekshege jaqin qilip awdarip beremen."
    )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        result = GoogleTranslator(source='auto', target='uz').translate(text)
        await update.message.reply_text(f"Awdarma:\n\n{result}")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Kechiring, awdariwda qatelik shiqti.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    app.run_polling()

if __name__ == "__main__":
    main()
