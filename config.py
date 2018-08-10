from prettyconf import config

NEWS_URL = 'http://www.gobiernodecanarias.org/educacion/web/'

DATABASE = config(
    'DATABASE',
    default='news.db'
)
MAX_NEWS_TO_SAVE_ON_DB = config(
    'MAX_NEWS_TO_SAVE_ON_DB',
    default='100',
    cast=config.eval
)
BOT_TOKEN = config(
    'BOT_TOKEN',
    default='put here the token of your bot'
)
CHANNEL_NAME = config(
    'CHANNEL_NAME',
    default='put here the telegram name of the channel (with @)'
)
