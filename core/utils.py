import difflib
import re

from slugify import slugify

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


def clean_text(text):
    # Dots or whitespaces on left
    text = re.sub(r'^[\s.]+', '', text)
    # Dots or whitespaces on right
    text = re.sub(r'[\s.]+$', '', text)
    # Remove square brackets -> conflict with markdown
    text = re.sub(r'[\[\]]+', '', text)

    return text


def tokenize(text):
    return map(slugify, re.findall(r'\w+', text))


def similarity_ratio(text1, text2):
    tokenized_text1 = list(
        {word for word in tokenize(text1) if word not in WORDS_TO_IGNORE}
    )
    tokenized_text2 = list(
        {word for word in tokenize(text2) if word not in WORDS_TO_IGNORE}
    )
    sm = difflib.SequenceMatcher(None, tokenized_text1, tokenized_text2)
    return sm.ratio()
