'''EduCanNews

Usage:
    main.py createdb
    main.py notify
'''
from docopt import docopt

from core.db import create_db, init_db
from core.news import News
from core.utils import init_logger

logger = init_logger()

arguments = docopt(__doc__)

if arguments['createdb']:
    create_db(force_delete=False, verbose=False)
elif arguments['notify']:
    educan_news = News(*init_db())
    educan_news.get_news()
    educan_news.sift_news()
    educan_news.dispatch_news()
