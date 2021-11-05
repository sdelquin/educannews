import os
import time
from urllib.parse import urljoin

import requests
import telegram
from bs4 import BeautifulSoup

import settings
from core import log, utils
from core.newsitem import NewsItem

logger = log.init_logger(__name__)


class News:
    def __init__(self, dbconn, dbcur):
        logger.info('Building News object')
        self.url = settings.NEWS_URL
        self.num_news_to_delete_when_rotating_db = (
            self._get_num_news_to_delete_when_rotating_db()
        )

        self.dbconn = dbconn
        self.dbcur = dbcur
        self.bot = telegram.Bot(token=settings.BOT_TOKEN)

    def _get_num_news_to_delete_when_rotating_db(self):
        return (
            1
            if settings.MAX_NEWS_TO_SAVE_ON_DB <= 2 * settings.ROUGH_NUM_NEWS_ON_FRONTPAGE
            else settings.MAX_NEWS_TO_SAVE_ON_DB // 2
        )

    def __str__(self):
        buffer = []
        for i, news_item in enumerate(self.news):
            buffer.append(f'{i + 1}) {news_item}')
        return os.linesep.join(buffer)

    def __parse_single_news(self, news):
        news_header = news.h3
        news_summary = news.find('div', 'txt_noticia')
        link = news_header.a

        # ensure url is absolute
        url = urljoin(settings.NEWS_URL, link['href'].strip())
        title = utils.clean_text(link.contents[4])
        date = utils.clean_text(link.find('span', 'fecha').string)
        category = utils.clean_text(link.find('span', 'categorias').string)
        summary = utils.clean_text(news_summary.text)

        return url, date, category, title, summary

    def get_news(self, max_news_to_retrieve=None):
        '''
        Estructura de las noticias:
        div.noticia
            ⌊ h3.titulo_novedad
                ⌊ a  -> (href)
                    ⌊ span.fecha
                    ⌊ span.categorias
            ⌊ div.txt_noticia
                ⌊ p
                ⌊ p
        '''

        logger.info('Getting news from web')
        self.news = []
        result = requests.get(self.url)
        soup = BeautifulSoup(result.content, features='html.parser')
        all_news = soup.find_all('div', 'noticia')

        logger.info('Parsing downloaded news')
        for news in list(reversed(all_news))[:max_news_to_retrieve]:
            url, date, category, title, summary = self.__parse_single_news(news)
            self.news.append(
                NewsItem(url, date, category, title, summary, self.dbconn, self.dbcur)
            )

        self._sift_news()

    def _sift_news(self):
        logger.info('Sifting news')
        self.news, news = [], self.news[:]
        for news_item in news:
            ni = news_item.is_already_exactly_saved()
            if ni:
                if ni['url'] == news_item.url:
                    logger.info(f'Ignoring already saved: {news_item}')
                    continue
                else:
                    # capture telegram message id to be edited with new url
                    news_item.tg_msg_id = ni['tg_msg_id']
            else:
                # news_item and similarity ratio
                ni, sr = news_item.is_already_similar_saved()
                if ni:
                    logger.info(f'Found similar news_item [{sr:.2f}]: {news_item}')
                    news_item.tg_msg_id = ni['tg_msg_id']
            self.news.append(news_item)

    def max_news_on_db_reached(self):
        return self.num_news_on_db == settings.MAX_NEWS_TO_SAVE_ON_DB

    @property
    def num_news_on_db(self):
        self.dbcur.execute("select count(*) as size from news")
        return self.dbcur.fetchone()['size']

    def rotate_db(self):
        self.dbcur.execute(
            f'''
            delete from news where rowid in
            (select rowid from news order by rowid limit
            {self.num_news_to_delete_when_rotating_db})
        '''
        )
        self.dbconn.commit()

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
            time.sleep(settings.DELAY_BETWEEN_TELEGRAM_DELIVERIES)

    def reset(self):
        """MAKE USE WITH ATTENTION. It will delete every news"""
        self.dbcur.execute('select * from news')
        for newsitem in self.dbcur.fetchall():
            self.bot.delete_message(settings.CHANNEL_NAME, newsitem['tg_msg_id'])
        self.dbcur.execute('delete from news')
        self.dbconn.commit()
        self.news = []
