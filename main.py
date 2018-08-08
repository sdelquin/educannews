import requests
from bs4 import BeautifulSoup
import re

result = requests.get('http://www.gobiernodecanarias.org/educacion/web/')
c = result.content

soup = BeautifulSoup(c, features='html.parser')
content = soup.find('form', 'frm_bloque_novedades_categorizadas').parent
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
    print(url, date, category, title, sep='\n')
