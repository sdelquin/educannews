import requests
from bs4 import BeautifulSoup

result = requests.get('http://www.gobiernodecanarias.org/educacion/web/')
c = result.content

soup = BeautifulSoup(c, features='html.parser')
form = soup.find('form', 'frm_bloque_novedades_categorizadas')
content = form.parent
all_news = content.find_all('div', 'noticia')
for news in all_news:
    a = news.h3.a
    spans = a.find_all('span')
    print(a['href'])
    print(spans[0].string)
    print(spans[1].string)
