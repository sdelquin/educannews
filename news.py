import requests
from bs4 import BeautifulSoup
import re
import pprint


class News:
    def __init__(self, url):
        self.url = url
        self.news = []

    def __str__(self):
        return pprint.pformat(self.news, indent=4)

    def get_news(self):
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
            self.news.append({
                'url': url,
                'date': date,
                'category': category,
                'title': title
            })
