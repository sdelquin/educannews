import re


def rstripwithdots(text):
    return re.sub(r'[\s.]+$', '', text)
