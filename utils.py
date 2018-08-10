import re
import logging
import logging.handlers
import config


def hash_category(category):
    return '#' + re.sub(r'\s*,\s*|\s+', '', category.title())


def rstripwithdots(text):
    return re.sub(r'[\s.]+$', '', text)


def init_logger(name='main'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        config.LOGFILE,
        maxBytes=config.LOGFILE_MAX_SIZE,
        backupCount=2
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)-6s: [%(levelname)-8s] %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
