import os

import pytest

from core.db import create_db
from core.news import News

TEST_DB_PATH = 'news.test.db'
NUM_NEWS_TO_TEST = 3


@pytest.fixture
def educan_news():
    dbconn, dbcur = create_db(TEST_DB_PATH, force_delete=True, verbose=False)
    educan_news = News(dbconn, dbcur)
    educan_news.get_news(NUM_NEWS_TO_TEST)
    educan_news.dispatch_news()
    yield educan_news
    educan_news.reset()
    os.remove(TEST_DB_PATH)


def test_telegram_sending(educan_news):
    assert len(educan_news.news) == educan_news.num_news_on_db


def test_telegram_editing(educan_news):
    newsitem = educan_news.news[0]
    educan_news.dbcur.execute("update news set url='' where rowid=1")
    educan_news.dbconn.commit()
    educan_news.get_news(NUM_NEWS_TO_TEST)
    educan_news.dispatch_news()
    educan_news.dbcur.execute("select * from news where rowid=1")
    assert newsitem.url == educan_news.dbcur.fetchone()['url']


def test_exact_news_found(educan_news):
    educan_news.get_news(NUM_NEWS_TO_TEST)
    educan_news.dispatch_news()
    assert len(educan_news.news) == 0


def test_similar_news_found(educan_news):
    newsitem = educan_news.news[0]
    educan_news.dbcur.execute(
        f"update news set title=';-{newsitem.title.upper()}-' where rowid=1"
    )
    educan_news.dbconn.commit()
    educan_news.get_news(NUM_NEWS_TO_TEST)
    educan_news.dispatch_news()
    assert len(educan_news.news) == 1
