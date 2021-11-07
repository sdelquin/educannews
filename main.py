import logzero
import typer

from core.db import create_db, init_db
from core.news import News
from core.utils import init_logger

logger = init_logger()
app = typer.Typer(add_completion=False)


@app.command()
def createdb():
    '''Create database.'''
    create_db(force_delete=False, verbose=False)


@app.command()
def notify(
    verbose: bool = typer.Option(
        False, '--verbose', '-v', show_default=False, help='Loglevel increased to debug'
    )
):
    '''Get and dispatch news.'''
    logger.setLevel(logzero.DEBUG if verbose else logzero.INFO)

    educan_news = News(*init_db())
    educan_news.get_news()
    educan_news.sift_news()
    educan_news.dispatch_news()


if __name__ == "__main__":
    app()
