import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = (
    "You are a professional translator. Translate the user's message into "
    "Karakalpak (Qaraqalpaq tili), using the Latin Karakalpak alphabet. "
    "Reply with ONLY the translation itself — no explanations, no quotes, "
    "no extra commentary. If the text is already in Karakalpak, lightly "
    "polish it and correct any grammar mistakes instead of leaving it unchanged."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalawma áleykum! 👋\n\n"
        "Men Qaraqalpaq awdarma botpan. Maǵan qálegen tildegi tekstti "
        "jiberiń, men onı Qaraqalpaq tiline awdarıp beremen.\n\n"
        "Jaqsı, endi bir sóylem jiberiń! ✍️"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Qálegen tildegi tekstti jiberiń — men onı Qaraqalpaqshaǵa "
        "awdarıp beremen.\n\n"
        "Buyrıqlar:\n"
        "/start — botti qayta iske túsiriw\n"
        "/help — járdem"
    )


async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text or not user_text.strip():
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_text}],
        )
        translation = response.content[0].text.strip()
        await update.message.reply_text(translation)
    except Exception as e:
        logger.error(f"Awdarıw qátesi: {e}")
        await update.message.reply_text(
            "Keshirim, awdarıwda qátelik júz berdi. Qайta urınıp kóriń."
        )


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN ortalıq ózgeriwshisi ornatılmaǵan!")
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY ortalıq ózgeriwshisi ornatılmaǵan!")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

    logger.info("Bot iske tústi...")
    app.run_polling()


if __name__ == "__main__":
    main()
