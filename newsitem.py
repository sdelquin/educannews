import re
import datetime
import time

import telegram

import log
import config
import utils

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

    def is_already_exactly_saved(self):
        # retrieve last seen news-item with the same title
        self.dbcur.execute(f"select * from news where title='{self.title}'")
        return self.dbcur.fetchone()

    def is_already_similar_saved(
            self, search_limit=config.ROUGH_NUM_NEWS_ON_FRONTPAGE):
        self.dbcur.execute('select * from news order by rowid desc')
        best_ratio, best_news_item = 0, None
        for news_item in self.dbcur.fetchall()[:search_limit]:
            ratio = utils.similarity_ratio(news_item['title'], self.title)
            if ratio > best_ratio:
                best_ratio = ratio
                best_news_item = news_item
        if best_ratio >= config.NEWS_SIMILARITY_THRESHOLD:
            return best_news_item, best_ratio
        else:
            return None, 0

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

    def update_on_db(self, fields=['title', 'url']):
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
    def is_announcement(self):
        return self.url == ''

    @property
    def as_markdown(self):
        if self.is_announcement:
            md = f'{self.title}. {self.category_as_hash}'
        else:
            md = f'[{self.title}.]({self.url}) {self.category_as_hash}'
        return md

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
