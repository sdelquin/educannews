import difflib
import re

from slugify import slugify

import config

PREPOSITIONS = [
    'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante',
    'en', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'segun', 'sin',
    'so', 'sobre', 'tras', 'versus', 'via'
]
ARTICLES = ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas']
DETERMINERS = [
    'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel',
    'aquella', 'aquellos', 'aquellas'
]
WORDS_TO_IGNORE = PREPOSITIONS + ARTICLES + DETERMINERS


def rstripwithdots(text):
    return re.sub(r'[\s.]+$', '', text)


def tokenize(text):
    return map(slugify, re.findall(r'\w+', text))


def similarity_ratio(text1, text2):
    tokenized_text1 = list({
        word
        for word in tokenize(text1) if word not in WORDS_TO_IGNORE
    })
    tokenized_text2 = list({
        word
        for word in tokenize(text2) if word not in WORDS_TO_IGNORE
    })
    sm = difflib.SequenceMatcher(None, tokenized_text1, tokenized_text2)
    return sm.ratio()


def replace_important(text):
    return re.sub(r'\[\s*IMPORTANTE\s*\]', config.EMOJI_FOR_IMPORTANT_NEWS,
                  text)

def remove_square_brackets(text):
    return re.sub(r'\[\s*([^\[\]]+)\s*\]', r'\1', text)
