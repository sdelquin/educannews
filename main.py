from news import News
import config

n = News(config.NEWS_URL, config.DATABASE)
n.get_news()
print(n.news2markdown())
