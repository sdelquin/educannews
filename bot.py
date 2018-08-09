import config
from telegram.ext import Updater, CommandHandler
from utils import add_chat, delete_chat


def register(bot, update):
    chat = update.message.chat
    if add_chat(chat):
        msg = ('✅ You have been successfuly REGISTERED '
               'to receive notifications!')
    else:
        msg = ('🚫 You can not register again. '
               'Already registered! 👍🏻')
    bot.send_message(
        chat_id=chat.id,
        text=msg
    )


def unregister(bot, update):
    chat = update.message.chat
    if delete_chat(chat):
        msg = ('✅ You have been successfuly UNREGISTERED '
               'from receiving notifications!')
    else:
        msg = ('🚫 You can not unregister again. '
               'Already unregistered! 👍🏻')
    bot.send_message(
        chat_id=chat.id,
        text=msg
    )


updater = Updater(config.BOT_TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler('register', register))
dp.add_handler(CommandHandler('unregister', unregister))

updater.start_polling()
updater.idle()
