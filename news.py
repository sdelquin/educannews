import requests
from bs4 import BeautifulSoup
import re
import pprint
import os
import sqlite3
import datetime


class News:
    def __init__(self, url, db):
        self.url = url
        self.dbconn = sqlite3.connect(db)
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
        for news in all_news:
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
            if not self.news_on_db(current_news):
                self.news.append(current_news)
                self.save_news(current_news)

    def news_on_db(self, news):
        self.dbcur.execute(f'''select * from news where
            (title='{news["title"]}') and
            (date='{news["date"]}') and
            (url='{news["url"]}') and
            (category='{news["category"]}')
        ''')
        return self.dbcur.fetchone()

    def save_news(self, news):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dbcur.execute(f'''insert into news values (
            '{news["title"]}',
            '{news["date"]}',
            '{news["url"]}',
            '{news["category"]}',
            '{now}'
        )''')
        self.dbconn.commit()

    def news2markdown(self):
        md = []
        for news in self.news:
            md.append(f'[{news["title"]}]({news["url"]})')
        return os.linesep.join(md)
