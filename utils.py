import difflib
import re
from slugify import slugify


def rstripwithdots(text):
    return re.sub(r'[\s.]+$', '', text)


def tokenize(text):
    return map(slugify, re.findall(r'\w+', text))


def similarity_ratio(text1, text2):
    words_in_text1 = list(tokenize(text1))
    words_in_text2 = list(tokenize(text2))
    sm = difflib.SequenceMatcher(None, words_in_text1, words_in_text2)
    return sm.ratio()
