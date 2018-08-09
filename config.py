from prettyconf import config

NEWS_URL = 'http://www.gobiernodecanarias.org/educacion/web/'
DATABASE = 'news.db'
MAX_NEWS_TO_SAVE_ON_DB = 100
BOT_TOKEN = config('BOT_TOKEN', default='put here the token of your bot')
USER_IDS = config(
    'USER_IDS',
    default='put here your Telegram user id',
    cast=config.list
 )
