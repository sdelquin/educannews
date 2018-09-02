import logging
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)-9s: [%(levelname)-8s] %(message)s'
        },
    },
    'handlers': {
        'logfile': {
            'level': 'INFO',
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'educannews.log',
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 1,
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['logfile'],
        'propagate': True
    },
}


def init_logger(name='main'):
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger(name)
    return logger
