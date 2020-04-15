import logging

import httpx
from dacite import from_dict

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from underflow.settings import settings
from underflow.stackoverflow import Question

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def help(update, context):
    """Echo the user message."""
    update.message.reply_text("Para realizar pesquisa, digite /ask <palavras chaves>")


def ask(update, context):
    """Realiza pesquisa no stack overflow usando api interna."""
    search_query = update.message.text[5:]
    logger.info(f"Search for {search_query}")
    result = httpx.post("http://localhost:8000/search", json={"query": search_query},)
    items = result.json()
    questions = [from_dict(Question, item) for item in items["results"]]

    if not questions:
        update.message.reply_text("Não foi encontrado nenhum resultado para a pesquisa")
        return

    for q in questions:
        msg = f"{q.title} | {q.answer_with_better_score().score} | {q.answer_with_better_score().link}"
        update.message.reply_text(msg)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = settings.tlg_token
    logger.info(f"token({token})")
    updater = Updater(token=token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("ask", ask))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - show help
    dp.add_handler(MessageHandler(Filters.text, help))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
