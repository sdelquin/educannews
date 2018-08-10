import config
import telegram
from telegram.ext import Updater, CommandHandler
import utils


def start(bot, update):
    msg = f'''
_¡Gracias sean dadas al Hacedor! Este baño de aceite me sentará muy bien. \
Me ha entrado tal cantidad de polvo que apenas puedo moverme._

No soy `C-3PO` pero sí un bot que puede hacerte la vida más fácil enviándote \
las novedades de la *Consejería de Educación y Universidades* del *Gobierno \
de Canarias* a tu Telegram de forma instantánea a cuando se publican en su \
[web]({config.NEWS_URL}).

*Comandos disponibles:*
/register - te registrará en el sistema para recibir notificaciones.
/unregister - te eliminará del sistema y dejarás de recibir notificaciones.
    '''
    bot.send_message(
        chat_id=update.message.chat_id,
        text=msg,
        parse_mode=telegram.ParseMode.MARKDOWN
    )


def register(bot, update):
    chat = update.message.chat
    if utils.add_chat(chat):
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
    if utils.delete_chat(chat):
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

dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('register', register))
dp.add_handler(CommandHandler('unregister', unregister))

updater.start_polling()
updater.idle()
