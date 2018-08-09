import requests
from bs4 import BeautifulSoup
import re


def get_news(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.content, features='html.parser')
    content = soup.find('form', 'frm_bloque_novedades_categorizadas').parent
    all_news = content.find_all('div', 'noticia')
    n = []
    for news in all_news:
        a = news.h3.a
        spans = a.find_all('span')
        url = a['href'].strip()
        date, category = (
            t.strip() for t in
            re.search(r'\[(.*)\].*\[(.*)\]', spans[0].string).groups()
        )
        title = spans[1].string.strip()
        n.append({
            'url': url,
            'date': date,
            'category': category,
            'title': title
        })
    return n


print(get_news('http://www.gobiernodecanarias.org/educacion/web/'))
