import re


def hash_category(category):
    return '#' + re.sub(r'\s*,\s*|\s+', '', category.title())


def rstripwithdots(text):
    return re.sub(r'[\s.]+$', '', text)
