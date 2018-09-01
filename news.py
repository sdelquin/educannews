import re
import sqlite3
import datetime
from urllib.parse import urljoin
import time
import os

import requests
from bs4 import BeautifulSoup
import telegram

import log
import utils
import config


logger = log.init_logger(__name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


dbconn = sqlite3.connect(config.DATABASE)
dbconn.row_factory = dict_factory
dbcur = dbconn.cursor()
bot = telegram.Bot(token=config.BOT_TOKEN)


class NewsItem:
    def __init__(self, url, date, category, title):
        self.url = url
        self.date = date
        self.category = category
        self.title = title
        self.tg_msg_id = None

    def __str__(self):
        return self.title

    def is_already_saved(self):
        # retrieve last seen news-item with the same title (ignore case)
        dbcur.execute(
            (f"select * from news where title='{self.title}' "
             "collate nocase order by rowid desc")
        )
        return dbcur.fetchone()

    def save_on_db(self, tg_msg_id):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%f')
        logger.info(f'Saving on DB: {self}')
        dbcur.execute(f'''insert into news values (
            '{self.title}',
            '{self.date}',
            '{self.url}',
            '{self.category}',
            '{now}',
            {tg_msg_id}
        )''')
        dbconn.commit()

    def update_on_db(self, fields=['url']):
        logger.info(f'Updating on DB: {self}')
        set_expr = ', '.join([f"{f} = '{getattr(self, f)}'" for f in fields])
        dbcur.execute(
            f"update news set {set_expr} where tg_msg_id = {self.tg_msg_id}"
        )
        dbconn.commit()

    @property
    def category_as_hash(self):
        return '#' + re.sub(r'\s*,\s*|\s+', '', self.category.title())

    @property
    def as_markdown(self):
        return f'[{self.title}.]({self.url}) {self.category_as_hash}'

    def send_msg(self):
        logger.info(f'Sending telegram message: {self}')
        m = None
        try:
            m = bot.send_message(
                chat_id=config.CHANNEL_NAME,
                text=self.as_markdown,
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
        except telegram.error.BadRequest:
            logger.exception('Ups! Something went wrong')
        except telegram.error.TimedOut:
            # message could be correctly delivered: https://goo.gl/TZ7kGR
            logger.exception('Ups! Something went wrong')
        return m

    def edit_msg(self):
        logger.info(f'Editing telegram message: {self}')
        m = None
        try:
            m = bot.edit_message_text(
                chat_id=config.CHANNEL_NAME,
                message_id=self.tg_msg_id,
                text=self.as_markdown + ' #editado',
                parse_mode=telegram.ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
        except telegram.error.BadRequest:
            logger.exception('Ups! Something went wrong')
        except telegram.error.TimedOut:
            logger.exception('Ups! Something went wrong')
        return m


class News:
    def __init__(self):
        logger.info('Building News object')
        self.url = config.NEWS_URL
        self.num_news_to_delete_when_rotating_db = \
            self._get_num_news_to_delete_when_rotating_db()

    def _get_num_news_to_delete_when_rotating_db(self):
        return 1 if config.MAX_NEWS_TO_SAVE_ON_DB <= 2 * \
            config.ROUGH_NUM_NEWS_ON_FRONTPAGE else \
            config.MAX_NEWS_TO_SAVE_ON_DB // 2

    def __str__(self):
        buffer = []
        for i, news_item in enumerate(self.news):
            buffer.append(f'{i + 1}) {news_item}')
        return os.linesep.join(buffer)

    def get_news(self):
        logger.info('Getting news from web')
        self.news = []
        result = requests.get(self.url)
        soup = BeautifulSoup(result.content, features='html.parser')
        content = soup.find(
            'form', 'frm_bloque_novedades_categorizadas'
        ).parent
        all_news = content.find_all('div', 'noticia')
        logger.info('Parsing downloaded news')
        for news in reversed(all_news):
            a = news.h3.a
            spans = a.find_all('span')
            # ensure url is absolute
            url = urljoin(config.NEWS_URL, a['href'].strip())
            date, category = (
                t.strip() for t in
                re.search(r'\[(.*)\].*\[(.*)\]', spans[0].string).groups()
            )
            title = spans[1].string.strip()
            # remove dots at the right
            category = utils.rstripwithdots(category)
            title = utils.rstripwithdots(title)

            self.news.append(NewsItem(url, date, category, title))
        self._sift_news()

    def _sift_news(self):
        logger.info('Sifting news')
        self.news, news = [], self.news[:]
        for news_item in news:
            r = news_item.is_already_saved()
            if r:
                if r['url'] == news_item.url:
                    logger.info(f'Ignoring already checked: {news_item}')
                    continue
                else:
                    # capture telegram message id to be edited with new url
                    news_item.tg_msg_id = r['tg_msg_id']
            self.news.append(news_item)

    def max_news_on_db_reached(self):
        return self.num_news_on_db == config.MAX_NEWS_TO_SAVE_ON_DB

    @property
    def num_news_on_db(self):
        dbcur.execute("select count(*) as size from news")
        return dbcur.fetchone()['size']

    def rotate_db(self):
        dbcur.execute(f'''
            delete from news where rowid in
            (select rowid from news order by rowid limit
            {self.num_news_to_delete_when_rotating_db})
        ''')
        dbconn.commit()

    def check_db_overflow(self):
        if self.max_news_on_db_reached():
            logger.warning('Reached max news in database. Rotating')
            self.rotate_db()

    def dispatch_news(self):
        for news_item in self.news:
            if news_item.tg_msg_id:
                if news_item.edit_msg():
                    news_item.update_on_db()
            else:
                msg = news_item.send_msg()
                if msg:
                    self.check_db_overflow()
                    news_item.save_on_db(msg.message_id)
            # ensure dispatching in right order and avoid timeout issues
            time.sleep(0.5)
