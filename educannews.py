'''EduCanNews

Usage:
    educannews.py createdb
    educannews.py notify
'''
from news import News
from docopt import docopt
from db import create_db, init_db

arguments = docopt(__doc__)
if arguments['createdb']:
    create_db()
elif arguments['notify']:
    educan_news = News(*init_db())
    educan_news.get_news()
    educan_news.dispatch_news()
