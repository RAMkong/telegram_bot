from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import tel_bot.constants as const
from telegram.ext import ApplicationBuilder


async def start_command(update: Update, context: CallbackContext):
    await update.message.reply_text("this is a LLMbot")


async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("i cannot help now")


async def custom_command(update: Update, context: CallbackContext):
    await update.message.reply_text("this is a custom command")


# responses

def handle_response(text: str) -> str:
    processed = text.lower()

    if "hello" in processed:
        return "yo sup"
    if "how are you" in processed:
        return "take a guess i am bot"
    if "tell me a joke" in processed:
        return "knock knock"

    return "ask me something i know"


async def handle_message(update: Update, context: CallbackContext):
    message_type = update.message.chat.type
    text = update.message.text

    print(f'User({update.message.from_user.id}) in {message_type}: "{text}"')

    response = handle_response(text)
    print("bot:", response)
    await update.message.reply_text(response)


async def error(update: Update, context: CallbackContext):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    app_builder = ApplicationBuilder()
    app_builder.token(const.token)

    app = app_builder.build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling.......')
    app.run_polling(poll_interval=3)