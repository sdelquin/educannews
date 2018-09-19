import re
import datetime
import time

import telegram

import log
import config

logger = log.init_logger(__name__)

THIRD_MODULES_EXCEPTION_MSG = 'Ups! Something went wrong'


class NewsItem:
    def __init__(self, url, date, category, title, dbconn, dbcur):
        self.url = url
        self.date = date
        self.category = category
        self.title = title
        self.tg_msg_id = None

        self.dbconn = dbconn
        self.dbcur = dbcur
        self.bot = telegram.Bot(token=config.BOT_TOKEN)

    def __str__(self):
        return self.title

    def is_already_saved(self):
        # retrieve last seen news-item with the same title (ignore case)
        self.dbcur.execute(
            (f"select * from news where title='{self.title}' "
             "collate nocase order by rowid desc")
        )
        return self.dbcur.fetchone()

    def save_on_db(self, tg_msg_id):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%f')
        logger.info(f'Saving on DB: {self}')
        self.dbcur.execute(f'''insert into news values (
            '{self.title}',
            '{self.date}',
            '{self.url}',
            '{self.category}',
            '{now}',
            {tg_msg_id}
        )''')
        self.dbconn.commit()

    def update_on_db(self, fields=['url']):
        logger.info(f'Updating on DB: {self}')
        set_expr = ', '.join([f"{f} = '{getattr(self, f)}'" for f in fields])
        self.dbcur.execute(
            f"update news set {set_expr} where tg_msg_id = {self.tg_msg_id}"
        )
        self.dbconn.commit()

    @property
    def category_as_hash(self):
        return '#' + re.sub(r'\s*,\s*|\s+', '', self.category.title())

    @property
    def as_markdown(self):
        return f'[{self.title}.]({self.url}) {self.category_as_hash}'

    def send_msg(self):
        m, retry = None, 0
        while (not m) and (retry <= config.NUM_TELEGRAM_RETRIES):
            retry_msg = f' (retry {retry})' if retry else ''
            logger.info(f'Sending telegram message{retry_msg}: {self}')
            try:
                m = self.bot.send_message(
                    chat_id=config.CHANNEL_NAME,
                    text=self.as_markdown,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=False,
                    timeout=config.TELEGRAM_READ_TIMEOUT
                )
            except telegram.error.BadRequest:
                logger.exception(THIRD_MODULES_EXCEPTION_MSG)
            except telegram.error.TimedOut:
                # message could be correctly delivered: https://goo.gl/TZ7kGR
                logger.exception(THIRD_MODULES_EXCEPTION_MSG)
                retry += 1
                time.sleep(config.DELAY_BETWEEN_TELEGRAM_DELIVERIES)
        return m

    def edit_msg(self):
        m, retry = None, 0
        while (not m) and (retry <= config.NUM_TELEGRAM_RETRIES):
            retry_msg = f' (retry {retry})' if retry else ''
            logger.info(f'Editing telegram message{retry_msg}: {self}')
            try:
                m = self.bot.edit_message_text(
                    chat_id=config.CHANNEL_NAME,
                    message_id=self.tg_msg_id,
                    text=self.as_markdown + ' #editado',
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=False,
                    timeout=config.TELEGRAM_READ_TIMEOUT
                )
            except telegram.error.BadRequest:
                logger.exception(THIRD_MODULES_EXCEPTION_MSG)
            except telegram.error.TimedOut:
                logger.exception(THIRD_MODULES_EXCEPTION_MSG)
                retry += 1
                time.sleep(config.DELAY_BETWEEN_TELEGRAM_DELIVERIES)
        return m
