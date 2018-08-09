import requests
from bs4 import BeautifulSoup
import re
import pprint
import os
import sqlite3
import datetime
import config


class News:
    def __init__(self):
        self.url = config.NEWS_URL
        self.dbconn = sqlite3.connect(config.DATABASE)
        self.dbcur = self.dbconn.cursor()

    def __str__(self):
        return pprint.pformat(self.news, indent=4)

    def get_news(self):
        self.news = []
        result = requests.get(self.url)
        soup = BeautifulSoup(result.content, features='html.parser')
        content = soup.find(
            'form', 'frm_bloque_novedades_categorizadas'
        ).parent
        all_news = content.find_all('div', 'noticia')
        for news in all_news[::-1]:
            a = news.h3.a
            spans = a.find_all('span')
            url = a['href'].strip()
            date, category = (
                t.strip() for t in
                re.search(r'\[(.*)\].*\[(.*)\]', spans[0].string).groups()
            )
            title = spans[1].string.strip()

            current_news = {
                'url': url,
                'date': date,
                'category': category,
                'title': title
            }
            if not self.check_if_news_on_db(current_news):
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
            # delete first saved news
            self.dbcur.execute(f'''delete from news where rowid =
                (select min(rowid) from news)
            ''')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        md = []
        for news in self.news:
            md.append(f'[{news["title"]}]({news["url"]})')
        return os.linesep.join(md)
