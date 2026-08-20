        import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import anthropic
import speech_recognition as sr
from pydub import AudioSegment

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = (
    "You are a professional translator. Translate the given text into "
    "Karakalpak (Qaraqalpaq tili), using the Latin alphabet. "
    "Reply with ONLY the translation itself — no extra commentary. "
    "If the text is already in Karakalpak, polish it and correct any grammar mistakes."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalawma áleykum! 👋\n\n"
        "Men Qaraqalpaq awdarma botpan. Maǵan qálegen tildegi tekst yamasa dawıs "
        "jiberiń, men onı Qaraqalpaq tiline awdarıp beremen.\n\n"
        "Jaqsı, endi bir sóylem jiberiń! ✍️"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Qálegen tildegi tekstti yamasa dawıs xabarındı jiberiń — men onı "
        "awdarıp beremen.\n\n"
        "Buyrıqlar:\n"
        "/start — botti qayta iske túsiriw\n"
        "/help — járdem"
    )


async def translate_text_and_reply(update: Update, user_text: str):
    if not user_text or not user_text.strip():
        return
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_text}]
        )
        translation = response.content[0].text.strip()
        await update.message.reply_text(translation)
    except Exception as e:
        logger.error(f"Awdarıw qátesi: {e}")
        await update.message.reply_text(
            "Keshirim, awdarıwda qátelik júz berdi. Qayta urınıp kóriń."
        )


async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await translate_text_and_reply(update, user_text)


async def translate_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        voice = update.message.voice or update.message.audio
        file = await context.bot.get_file(voice.file_id)

        ogg_path = f"/tmp/{voice.file_id}.ogg"
        wav_path = f"/tmp/{voice.file_id}.wav"
        await file.download_to_drive(ogg_path)

        audio = AudioSegment.from_file(ogg_path)
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data, language="ru-RU")

        os.remove(ogg_path)
        os.remove(wav_path)

        await translate_text_and_reply(update, recognized_text)
    except Exception as e:
        logger.error(f"Dawıs qátesi: {e}")
        await update.message.reply_text(
            "Keshirim, dawıstı tanıp bolmadı. Qayta urınıp kóriń yamasa anıqlaw ushın sóyleń."
        )


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN ortalıq ózgeriwshisi jоq")
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY ortalıq ózgeriwshisi jоq")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, translate_voice))

    logger.info("Bot iske tústi...")
    app.run_polling()


if __name__ == "__main__":
    main()
