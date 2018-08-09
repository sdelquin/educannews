from news import News

n = News('http://www.gobiernodecanarias.org/educacion/web/')
n.get_news()
print(n)
