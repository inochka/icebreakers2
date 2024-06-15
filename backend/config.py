import logging.config
import os
from pathlib import Path

backend_base_dir = Path(__file__).parent
tiffs_dir = backend_base_dir.parent / "tiffs"
json_dir = backend_base_dir / "data/json_data"

recalculate_loaded = False  # нужно ли пересчитывать при старте уже имеющиеся шаблоны

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