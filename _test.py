import os

import pytest

from news import News
from db import create_db

TEST_DB_PATH = 'news.test.db'
NUM_NEWS_TO_TEST = 3


@pytest.fixture(scope='module')
def db_handlers():
    yield create_db(TEST_DB_PATH, force_delete=True, verbose=False)
    # os.remove(TEST_DB_PATH)


def test_all(db_handlers):
    dbconn, dbcur = db_handlers
    educan_news = News(dbconn, dbcur)
    # test telegram sending
    educan_news.get_news(NUM_NEWS_TO_TEST)
    educan_news.dispatch_news()
    assert len(educan_news.news) == educan_news.num_news_on_db
    # test telegram editing
    newsitem = educan_news.news[0]
    dbcur.execute("update news set url='' where rowid=1")
    dbconn.commit()
    educan_news.get_news(NUM_NEWS_TO_TEST)
    educan_news.dispatch_news()
    dbcur.execute("select * from news where rowid=1")
    assert newsitem.url == dbcur.fetchone()['url']
    # test case insensitive messages
    newsitem = educan_news.news[0]
    dbcur.execute(
        f"update news set title='{newsitem.title.upper()}' where rowid=1"
    )
    dbconn.commit()
    educan_news.get_news(NUM_NEWS_TO_TEST)
    educan_news.dispatch_news()
    assert len(educan_news.news) == 0
