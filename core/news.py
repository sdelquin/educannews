import datetime
import os
import time
from urllib.parse import urljoin

import bs4
import dateutil
import requests
import telegram
from logzero import logger

import settings
from core import utils
from core.newsitem import NewsItem


class News:
    def __init__(self, dbconn, dbcur):
        logger.info('Building News object')
        self.url = settings.NEWS_URL
        self.num_news_to_delete_when_rotating_db = self._get_num_news_to_delete_when_rotating_db()

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

    @staticmethod
    def __parse_news_date(date: bs4.element.Tag | None) -> datetime.date:
        try:
            return dateutil.parser.parse(date.text.strip(), dayfirst=True).date()
        except (dateutil.parser.ParserError, AttributeError) as err:
            logger.error('Error parsing date!')
            logger.exception(err)
            return datetime.date.today()

    @staticmethod
    def __parse_news_topic(topic: bs4.element.Tag | None) -> str:
        try:
            return utils.clean_text(topic.text)
        except AttributeError as err:
            logger.error('Error parsing topic!')
            logger.exception(err)
            return settings.DEFAULT_TOPIC

    @staticmethod
    def __parse_news_title(title: bs4.element.Tag | None) -> str:
        try:
            return utils.clean_text(title.text)
        except AttributeError as err:
            logger.error('Error parsing title!')
            logger.exception(err)
            return settings.DEFAULT_TITLE

    @staticmethod
    def __parse_news_summary(summary: bs4.element.Tag | None) -> str:
        try:
            return utils.clean_text(summary.text)
        except AttributeError as err:
            logger.error('Error parsing summary!')
            logger.exception(err)
            return settings.DEFAULT_SUMMARY

    def parse_news(self, news: bs4.element.Tag) -> dict:
        """
        Estructura de una noticia:
        li.evento (news)
            ├ div.eventoFecha (date)
            ├ div.eventoCategoria (topic)
            ├ h5
            │   └ a (title)
            └ div.textoNovedad (summary)
        """
        date = self.__parse_news_date(news.select_one('div.eventoFecha'))
        topic = self.__parse_news_topic(news.select_one('div.eventoCategoria'))
        title = self.__parse_news_title(news.select_one('h5'))
        summary = self.__parse_news_summary(news.select_one('div.textoNovedad'))

        if link := news.select_one('h5 a'):
            # ensure url is absolute
            url = urljoin(settings.NEWS_URL, link['href'].strip())
        else:
            logger.warning('No link found for news item. Using default url')
            url = settings.NEWS_URL

        return dict(url=url, date=date, topic=topic, title=title, summary=summary)

    def get_news(self, max_news_to_retrieve=settings.NEWS_WINDOW_SIZE):
        logger.info('Getting news from web')
        self.news = []
        response = requests.get(self.url)
        soup = bs4.BeautifulSoup(response.content, features='html.parser')
        all_news = soup.find_all('li', 'evento')

        logger.info('Parsing downloaded news')
        staged_news = reversed(list(all_news)[:max_news_to_retrieve])
        for news in staged_news:
            try:
                news_details = self.parse_news(news)
                if utils.check_if_news_has_to_be_ignored(news_details['title']):
                    logger.warning(f'Marked to be ignored: {news_details["title"]}')
                    continue
            except AttributeError as err:
                logger.error(f'Error parsing {news}')
                logger.exception(err)
            else:
                self.news.append(NewsItem(**news_details, dbconn=self.dbconn, dbcur=self.dbcur))

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
        self.dbcur.execute('select count(*) as size from news')
        return self.dbcur.fetchone()['size']

    def rotate_db(self):
        self.dbcur.execute(
            f"""
            delete from news where rowid in
            (select rowid from news order by rowid limit
            {self.num_news_to_delete_when_rotating_db})
        """
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
        """MAKE USE WITH ATTENTION. It will delete every news"""
        logger.warning('Resetting database!')
        self.dbcur.execute('select * from news')
        for newsitem in self.dbcur.fetchall():
            self.bot.delete_message(settings.CHANNEL_NAME, newsitem['tg_msg_id'])
        self.dbcur.execute('delete from news')
        self.dbconn.commit()
        self.news = []
