from pathlib import Path

from prettyconf import config

PROJECT_DIR = Path(__file__).parent
PROJECT_NAME = PROJECT_DIR.name

NEWS_URL = config('NEWS_URL', default='https://www.gobiernodecanarias.org/educacion/web/')
DATABASE = PROJECT_DIR / config('DATABASE', default='news.db')
MAX_NEWS_TO_SAVE_ON_DB = config('MAX_NEWS_TO_SAVE_ON_DB', default=100, cast=int)
ROUGH_NUM_NEWS_ON_FRONTPAGE = config('ROUGH_NUM_NEWS_ON_FRONTPAGE', default=10, cast=int)
BOT_TOKEN = config('BOT_TOKEN', default='put here the token of your bot')
CHANNEL_NAME = config(
    'CHANNEL_NAME', default='put here the telegram name of the channel (with @)'
)
DELAY_BETWEEN_TELEGRAM_DELIVERIES = config(  # in seconds
    'DELAY_BETWEEN_TELEGRAM_DELIVERIES', default=1, cast=float
)
NUM_TELEGRAM_RETRIES = config('NUM_TELEGRAM_RETRIES', default=3, cast=int)
TELEGRAM_READ_TIMEOUT = config('TELEGRAM_READ_TIMEOUT', default=15, cast=int)
NEWS_SIMILARITY_THRESHOLD = config('NEWS_SIMILARITY_THRESHOLD', default=0.85, cast=float)
EMOJI_FOR_IMPORTANT_NEWS = config('EMOJI_FOR_IMPORTANT_NEWS', default='📣')

LOGFILE = config('LOGFILE', default=PROJECT_DIR / (PROJECT_NAME + '.log'))
LOGFILE_SIZE = config('LOGFILE_SIZE', cast=float, default=1e6)
LOGFILE_BACKUP_COUNT = config('LOGFILE_BACKUP_COUNT', cast=int, default=3)