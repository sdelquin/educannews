import difflib
import re

import logzero
from slugify import slugify

import settings

PREPOSITIONS = [
    'a',
    'ante',
    'bajo',
    'cabe',
    'con',
    'contra',
    'de',
    'desde',
    'durante',
    'en',
    'entre',
    'hacia',
    'hasta',
    'mediante',
    'para',
    'por',
    'segun',
    'sin',
    'so',
    'sobre',
    'tras',
    'versus',
    'via',
]
ARTICLES = ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas']
DETERMINERS = [
    'este',
    'esta',
    'estos',
    'estas',
    'ese',
    'esa',
    'esos',
    'esas',
    'aquel',
    'aquella',
    'aquellos',
    'aquellas',
]
WORDS_TO_IGNORE = PREPOSITIONS + ARTICLES + DETERMINERS


def init_logger():
    console_logformat = (
        '%(asctime)s '
        '%(color)s'
        '[%(levelname)-8s] '
        '%(end_color)s '
        '%(message)s '
        '%(color)s'
        '(%(filename)s:%(lineno)d)'
        '%(end_color)s'
    )
    # remove colors on logfile
    file_logformat = re.sub(r'%\((end_)?color\)s', '', console_logformat)

    console_formatter = logzero.LogFormatter(fmt=console_logformat)
    file_formatter = logzero.LogFormatter(fmt=file_logformat)
    logzero.setup_default_logger(formatter=console_formatter)
    logzero.logfile(
        settings.LOGFILE,
        maxBytes=settings.LOGFILE_SIZE,
        backupCount=settings.LOGFILE_BACKUP_COUNT,
        formatter=file_formatter,
    )
    return logzero.logger


def clean_text(text):
    # Dots or whitespaces on left
    text = re.sub(r'^[\s.]+', '', text)
    # Dots or whitespaces on right
    text = re.sub(r'[\s.]+$', '', text)
    # Escape square brackets -> conflict with markdown
    # https://stackoverflow.com/a/49924429
    text = text.replace('[', '\\[')

    return text


def tokenize(text):
    return map(slugify, re.findall(r'\w+', text))


def similarity_ratio(text1, text2):
    tokenized_text1 = list({word for word in tokenize(text1) if word not in WORDS_TO_IGNORE})
    tokenized_text2 = list({word for word in tokenize(text2) if word not in WORDS_TO_IGNORE})
    sm = difflib.SequenceMatcher(None, tokenized_text1, tokenized_text2)
    return sm.ratio()


def check_if_news_has_to_be_ignored(
    title: str, news_to_ignore: list[str] = settings.NEWS_TO_IGNORE
) -> bool:
    for news_title in news_to_ignore:
        if title.startswith(news_title):
            return True
    return False

def fix_markdown(text: str) -> str:
    MEANING_CHARS = '_'
    
    for char in MEANING_CHARS:
        text = text.replace(char, '')
    
    return text
