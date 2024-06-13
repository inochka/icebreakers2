import logging.config
import os


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {process:d} {thread:d} {module} {funcName} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': "verbose"
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'default': {
            'handlers': ['console'],
            'level': os.getenv('PYTHON_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING)