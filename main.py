
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram_bot import *

prompt:str = ""


if __name__ == "__main__":
    token_init()

    load_dotenv()
    setup_llama_index()

    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        # Persiapkan format mention (@username) dengan aman
    raw_username = os.environ.get("TELEGRAM_BOT_USERNAME", "")
    bot_username = raw_username.replace("@", "")
    bot_mention = f"@{bot_username}"

    app = Application.builder().token(telegram_bot_token).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.PDF, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)