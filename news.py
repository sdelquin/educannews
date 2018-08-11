import requests
from bs4 import BeautifulSoup
import re
import pprint
import sqlite3
import datetime
import config
import telegram
from urllib.parse import urljoin
import utils
import time


logger = utils.init_logger(__name__)

dbconn = sqlite3.connect(config.DATABASE)
dbcur = dbconn.cursor()
bot = telegram.Bot(token=config.BOT_TOKEN)


class NewsItem:
    def __init__(self, url, date, category, title):
        self.url = url
        self.date = date
        self.category = category
        self.title = title

    def __str__(self):
        return self.title

    def is_already_saved(self):
        dbcur.execute(f'''select * from news where
            (title='{self.title}') and
            (date='{self.date}') and
            (url='{self.url}') and
            (category='{self.category}')
        ''')
        return dbcur.fetchone()

    def save(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%f')
        logger.info(f'Saving: {self}')
        dbcur.execute(f'''insert into news values (
            '{self.title}',
            '{self.date}',
            '{self.url}',
            '{self.category}',
            '{now}'
        )''')
        dbconn.commit()

    @property
    def category_as_hash(self):
        return '#' + re.sub(r'\s*,\s*|\s+', '', self.category.title())

    @property
    def as_markdown(self):
        return f'[{self.title}.]({self.url}) {self.category_as_hash}'

    def send(self):
        logger.info(f'Sending {self}')
        bot.send_message(
            chat_id=config.CHANNEL_NAME,
            text=self.as_markdown,
            parse_mode=telegram.ParseMode.MARKDOWN
        )


class News:
    def __init__(self):
        logger.info('Building News object...')
        self.url = config.NEWS_URL

    def __str__(self):
        return pprint.pformat(self.news, indent=4)

    def get_news(self):
        logger.info('Getting news from web...')
        self.news = []
        result = requests.get(self.url)
        soup = BeautifulSoup(result.content, features='html.parser')
        content = soup.find(
            'form', 'frm_bloque_novedades_categorizadas'
        ).parent
        all_news = content.find_all('div', 'noticia')
        logger.info('Parsing downloaded news...')
        for news in all_news[::-1]:
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

            # manage current news item
            news_item = NewsItem(url, date, category, title)
            if news_item.is_already_saved():
                logger.info(f'Ignoring already checked: {news_item}')
            else:
                self.news.append(news_item)
                if self.max_news_on_db_reached():
                    logger.warning('Reached max news in database. Rotating...')
                    self.rotate_db()
                news_item.save()

    def max_news_on_db_reached(self):
        return self.num_news_on_db == config.MAX_NEWS_TO_SAVE_ON_DB

    @property
    def num_news_on_db(self):
        dbcur.execute("select count(*) from news")
        return dbcur.fetchone()[0]

    def rotate_db(self):
        # delete first saved news
        dbcur.execute(f'''delete from news where rowid =
            (select min(rowid) from news)
        ''')

    def send_news(self):
        if self.news:
            for news_item in self.news:
                news_item.send()
                time.sleep(0.1)
        else:
            logger.info('No news! Good news!')
