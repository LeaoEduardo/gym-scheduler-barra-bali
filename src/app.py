import sys

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from src import BOT_TOKEN, WEBHOOK, PORT
from src.bot import Bot

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    schedule_path = sys.argv[1]
    if schedule_path != None:
        bot = Bot(schedule_path)
    else:
        bot = Bot

    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("horarios", bot.list_schedule))
    # dp.add_handler(CommandHandler("marcar_musc", schedule_musc))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, bot.fallback))

    # # log all errors
    # dp.add_error_handler(error)

    # Uncomment this part when deploing to heroku
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=BOT_TOKEN,
    #                       webhook_url=WEBHOOK + BOT_TOKEN)

    # Uncomment to test locally
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()