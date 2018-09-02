'''EduCanNews

Usage:
    educannews.py createdb
    educannews.py notify
'''
from news import News
from docopt import docopt
from db import create_db

arguments = docopt(__doc__)
if arguments['createdb']:
    create_db()
elif arguments['notify']:
    educan_news = News()
    educan_news.get_news()
    educan_news.dispatch_news()
