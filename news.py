import requests
from bs4 import BeautifulSoup
import re
import pprint
import os
import sqlite3
import datetime
import config
import telegram
from urllib.parse import urljoin
import utils


logger = utils.init_logger(__name__)


class News:
    def __init__(self):
        logger.info('Building News object...')
        self.url = config.NEWS_URL
        self.dbconn = sqlite3.connect(config.DATABASE)
        self.dbcur = self.dbconn.cursor()
        self.bot = telegram.Bot(token=config.BOT_TOKEN)

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

            current_news = {
                'url': url,
                'date': date,
                'category': category,
                'title': title
            }
            if self.check_if_news_on_db(current_news):
                logger.info(
                    f'Ignoring already checked: {current_news["title"]}'
                )
            else:
                self.news.append(current_news)
                self.save_news(current_news)

    def check_if_news_on_db(self, news):
        self.dbcur.execute(f'''select * from news where
            (title='{news["title"]}') and
            (date='{news["date"]}') and
            (url='{news["url"]}') and
            (category='{news["category"]}')
        ''')
        return self.dbcur.fetchone()

    def save_news(self, news):
        if self.get_num_news_on_db() == config.MAX_NEWS_TO_SAVE_ON_DB:
            logger.warning('Reached max window size in database. Rotating...')
            # delete first saved news
            self.dbcur.execute(f'''delete from news where rowid =
                (select min(rowid) from news)
            ''')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%f')
        logger.info(f'Saving: {news["title"]}')
        self.dbcur.execute(f'''insert into news values (
            '{news["title"]}',
            '{news["date"]}',
            '{news["url"]}',
            '{news["category"]}',
            '{now}'
        )''')
        self.dbconn.commit()

    def get_num_news_on_db(self):
        self.dbcur.execute("select count(*) from news")
        return self.dbcur.fetchone()[0]

    def news2markdown(self):
        logger.info('Converting news to markdown...')
        md = []
        for news in self.news:
            category = utils.hash_category(news['category'])
            md.append(
                f'[{news["title"]}.]({news["url"]}) {category}'
            )
        return (os.linesep * 2).join(md)

    def send_news(self):
        if self.news:
            msg = self.news2markdown()
            logger.info(f'Sending {len(self.news)} saved news...')
            self.bot.send_message(
                chat_id=config.CHANNEL_NAME,
                text=msg,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
        else:
            logger.info('No news! Good news!')
