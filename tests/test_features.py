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
    educan_news.sift_news()
    educan_news.dispatch_news()
    yield educan_news
    educan_news.reset()
    os.remove(TEST_DB_PATH)


def test_telegram_sending(educan_news):
    assert len(educan_news.news) == educan_news.num_news_on_db


def test_telegram_editing(educan_news):
    educan_news.dbcur.execute("select * from news where rowid=1")
    existing_newsitem = educan_news.dbcur.fetchone()

    educan_news.get_news(NUM_NEWS_TO_TEST)
    new_url = 'https://example.com'
    educan_news.news[0].url = new_url
    educan_news.sift_news()
    educan_news.dispatch_news()

    educan_news.dbcur.execute("select * from news where rowid=1")
    incoming_newsitem = educan_news.dbcur.fetchone()

    assert len(educan_news.news) == 1
    assert incoming_newsitem['tg_msg_id'] == existing_newsitem['tg_msg_id']
    assert incoming_newsitem['title'] == existing_newsitem['title']
    assert incoming_newsitem['summary'] == existing_newsitem['summary']
    assert incoming_newsitem['url'] == new_url


def test_exact_news_found(educan_news):
    educan_news.get_news(NUM_NEWS_TO_TEST)
    educan_news.dispatch_news()
    educan_news.sift_news()
    assert len(educan_news.news) == 0


def test_similar_news_found(educan_news):
    educan_news.dbcur.execute("select * from news where rowid=1")
    existing_newsitem = educan_news.dbcur.fetchone()

    educan_news.get_news(NUM_NEWS_TO_TEST)
    new_title = f";-{existing_newsitem['title'].upper()}-"
    educan_news.news[0].title = new_title
    educan_news.sift_news()
    educan_news.dispatch_news()

    educan_news.dbcur.execute("select * from news where rowid=1")
    incoming_newsitem = educan_news.dbcur.fetchone()

    assert len(educan_news.news) == 1
    assert incoming_newsitem['tg_msg_id'] == existing_newsitem['tg_msg_id']
    assert incoming_newsitem['url'] == existing_newsitem['url']
    assert incoming_newsitem['summary'] == existing_newsitem['summary']
    assert incoming_newsitem['title'] == new_title
