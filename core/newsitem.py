import datetime
import re
import time

import telegram
from logzero import logger

import settings
from core import utils

THIRD_MODULES_EXCEPTION_MSG = 'Ups! Something went wrong'


class NewsItem:
    def __init__(
        self,
        url: str,
        date: datetime.date,
        topics: list[str],
        title: str,
        summary: str,
        dbconn,
        dbcur,
    ):
        self.url = url
        self.date = date
        self.topics = topics
        self.title = title
        self.summary = summary
        self.tg_msg_id = None

        self.dbconn = dbconn
        self.dbcur = dbcur
        self.bot = telegram.Bot(token=settings.BOT_TOKEN)

    def __str__(self):
        return self.title

    def __repr__(self):
        buf = [self.title, self.url]
        return '\n'.join(buf)

    @property
    def fdate(self) -> str:
        return self.date.strftime('%d/%m/%Y')

    @property
    def topics_as_hashtags(self) -> str:
        return ' '.join(f"#{re.sub(r'[ .,;:]', '', topic.title())}" for topic in self.topics)

    @property
    def as_markdown(self) -> str:
        return f"""✨ {self.fdate} {self.topics_as_hashtags}

[{self.title}]({self.url})
_{utils.fix_markdown(self.summary)}_"""

    def is_saved_with_same_title(self):
        # retrieve last seen news-item with the same title
        self.dbcur.execute(f"select * from news where title='{self.title}'")
        return self.dbcur.fetchone()

    def is_saved_with_similar_title(self, search_limit=settings.NEWS_WINDOW_SIZE):
        self.dbcur.execute('select * from news order by rowid desc')
        best_ratio, best_news_item = 0, None
        for news_item in self.dbcur.fetchall()[:search_limit]:
            ratio = utils.similarity_ratio(news_item['title'], self.title)
            if ratio > best_ratio:
                best_ratio = ratio
                best_news_item = news_item
        if best_ratio >= settings.NEWS_SIMILARITY_THRESHOLD:
            return best_news_item, best_ratio
        else:
            return None, 0

    def save_on_db(self, tg_msg_id):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%f')
        logger.info(f'Saving on DB: {self}')
        self.dbcur.execute(
            'insert into news values (?, ?, ?, ?, ?, ?, ?)',
            (
                self.title,
                self.fdate,
                self.topics_as_hashtags,
                self.url,
                self.summary,
                now,
                tg_msg_id,
            ),
        )
        self.dbconn.commit()

    def update_on_db(
        self,
        fields=dict(
            title='title', date='fdate', topics='topics_as_hashtags', url='url', summary='summary'
        ),
    ):
        logger.info(f'Updating on DB: {self}')
        set_expr = ', '.join(
            [f"{db_field} = '{getattr(self, obj_field)}'" for db_field, obj_field in fields.items()]
        )
        self.dbcur.execute(f'update news set {set_expr} where tg_msg_id = {self.tg_msg_id}')
        self.dbconn.commit()

    def send_msg(self):
        m, retry = None, 0
        while (not m) and (retry <= settings.NUM_TELEGRAM_RETRIES):
            retry_msg = f' (retry {retry})' if retry else ''
            logger.info(f'Sending telegram message{retry_msg}: {self}')
            print(self.as_markdown)
            try:
                m = self.bot.send_message(
                    chat_id=settings.CHANNEL_NAME,
                    text=self.as_markdown,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=False,
                    timeout=settings.TELEGRAM_READ_TIMEOUT,
                )
            except telegram.error.TelegramError:
                # message could be correctly delivered: https://goo.gl/TZ7kGR
                logger.exception(THIRD_MODULES_EXCEPTION_MSG)
                retry += 1
                time.sleep(settings.DELAY_BETWEEN_TELEGRAM_DELIVERIES)
        return m

    def edit_msg(self):
        m, retry = None, 0
        while (not m) and (retry <= settings.NUM_TELEGRAM_RETRIES):
            retry_msg = f' (retry {retry})' if retry else ''
            logger.info(f'Editing telegram message{retry_msg}: {self}')
            try:
                m = self.bot.edit_message_text(
                    chat_id=settings.CHANNEL_NAME,
                    message_id=self.tg_msg_id,
                    text=self.as_markdown,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    disable_web_page_preview=False,
                    timeout=settings.TELEGRAM_READ_TIMEOUT,
                )
            except telegram.error.TelegramError:
                logger.exception(THIRD_MODULES_EXCEPTION_MSG)
                retry += 1
                time.sleep(settings.DELAY_BETWEEN_TELEGRAM_DELIVERIES)
        return m
