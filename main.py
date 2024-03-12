import os
import requests
from pydub import AudioSegment
import speech_recognition as sr
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import tel_bot.constants as const
from haystack.components.generators.chat import HuggingFaceTGIChatGenerator
from haystack.dataclasses import ChatMessage

# Last 10 chat conversations
msg = []

# Set Hugging Face API token
hf_token = const.hf_token
# Initialize Hugging Face Chat Generator
generator = HuggingFaceTGIChatGenerator(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    generation_kwargs={"max_new_tokens": 350},
)

generator.warm_up()

# Initialize Telegram Bot
TOKEN = const.token
app = Application.builder().token(TOKEN).build()



# Start command
async def start(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to my bot What do you need help with?")


# Help command
async def help(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="what are you waiting for ask something \nYou can also send voice messages here")


# Handle text messages
async def handle_text(update: Update, context):
    msg.append(ChatMessage.from_user(update.message.text))
    response = generator.run(messages=msg)
    msg.append(response["replies"][0])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response["replies"][0].content)
    if len(msg) > 20:
        msg.pop(0)
        msg.pop(0)


# Handle voice messages
async def handle_voice(update: Update, context):
    # Download voice message
    voice_file = context.bot.get_file(update.message.voice.file_id)
    file = requests.get("https://api.telegram.org/file/bot{0}/{1}".format(TOKEN, voice_file.file_path))
    with open("audio.ogg", "wb") as f:
        f.write(file.content)

    # Convert voice message to .wav format
    sound = AudioSegment.from_file("audio.ogg", format="ogg")
    sound.export("audio.wav", format="wav")

    # Convert voice meassage to text message
    recognizer = sr.Recognizer()
    with sr.AudioFile("audio.wav") as source:
        audio_file = recognizer.record(source)
        query = recognizer.recognize_google(audio_file)

    # Get response from Mistral bot
    msg.append(ChatMessage.from_user(query))
    response = generator.run(messages=msg)
    msg.append(response["replies"][0])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response["replies"][0].content)

    os.remove("audio.ogg")
    os.remove("audio.wav")
    if len(msg) > 20:
        msg.pop(0)
        msg.pop(0)


# Add handlers
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
app.add_handler(MessageHandler(filters._Voice, handle_voice))


if __name__ == "__main__":
    print("Bot is running...")
    print("Press Ctrl + C to stop bot")
    app.run_polling()
