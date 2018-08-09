from news import News
import config

n = News(config.NEWS_URL)
n.get_news()
print(n)
