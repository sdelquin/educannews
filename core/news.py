import os
import time
from urllib.parse import urljoin

import requests
import telegram
from bs4 import BeautifulSoup
from logzero import logger

import settings
from core import utils
from core.newsitem import NewsItem


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
            if settings.MAX_NEWS_TO_SAVE_ON_DB <= 2 * settings.NEWS_WINDOW_SIZE
            else settings.MAX_NEWS_TO_SAVE_ON_DB // 2
        )

    def __str__(self):
        buffer = []
        for i, news_item in enumerate(self.news):
            buffer.append(f'{i + 1}) {news_item}')
        return os.linesep.join(buffer)

    def __parse_single_news(self, news):
        '''
        Estructura de una noticia:
        news
          ⌊ a
              ⌊ h5 (titulo)
              ⌊ div (resumen)
        '''
        title = utils.clean_text(news.a.h5.text)
        summary = utils.clean_text(news.a.div.text)
        # ensure url is absolute
        url = urljoin(settings.NEWS_URL, news.a['href'].strip())

        return url, title, summary

    def get_news(self, max_news_to_retrieve=settings.NEWS_WINDOW_SIZE):
        '''
        Estructura de las noticias:
        ul.eventos-listado
        ⌊ li.evento
            ⌊ a
                ⌊ h5 (titulo)
                ⌊ div (resumen)
        '''

        logger.info('Getting news from web')
        self.news = []
        result = requests.get(self.url)
        soup = BeautifulSoup(result.content, features='html.parser')
        all_news = soup.find_all('li', 'evento')

        logger.info('Parsing downloaded news')
        staged_news = reversed(list(all_news)[:max_news_to_retrieve])
        for news in staged_news:
            url, title, summary = self.__parse_single_news(news)
            self.news.append(NewsItem(url, title, summary, self.dbconn, self.dbcur))

    def sift_news(self):
        logger.info('Sifting (filtering) news')
        self.news, news = [], self.news[:]
        for news_item in news:
            if ni := news_item.is_saved_with_same_title():
                if all(
                    (
                        ni['url'] == news_item.url,
                        ni['summary'] == news_item.summary,
                    )
                ):
                    logger.debug(f'Ignoring already saved: {news_item}')
                    continue
                else:
                    # capture telegram message id to be edited with new fields
                    logger.debug(f'Changes detected! Marking to be edited: {news_item}')
                    news_item.tg_msg_id = ni['tg_msg_id']
            else:
                # news_item and similarity ratio
                ni, sr = news_item.is_saved_with_similar_title()
                if ni:
                    logger.debug(f'Found similar news_item [{sr:.2f}]: {news_item}')
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
        logger.info('Dispatching news')
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
        '''MAKE USE WITH ATTENTION. It will delete every news'''
        logger.warning('Resetting database!')
        self.dbcur.execute('select * from news')
        for newsitem in self.dbcur.fetchall():
            self.bot.delete_message(settings.CHANNEL_NAME, newsitem['tg_msg_id'])
        self.dbcur.execute('delete from news')
        self.dbconn.commit()
        self.news = []
