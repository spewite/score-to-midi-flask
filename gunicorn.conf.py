import logging
from logging.handlers import SysLogHandler
import socket

# Basic Gunicorn configuration
bind = ":5000"
workers = 3
worker_class = "sync"
loglevel = "info"

# Local log files (keep these for backup)
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
access_log_format = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
capture_output = True

# Papertrail configuration
logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'papertrail': {
            'format': '%(asctime)s [GUNICORN] %(levelname)s [%(process)d]: %(message)s',
            'datefmt': '%b %d %H:%M:%S',
        },
    },
    'handlers': {
        'papertrail': {
            'class': 'logging.handlers.SysLogHandler',
            'address': ('logs6.papertrailapp.com', 23995),
            'socktype': socket.SOCK_DGRAM,
            'formatter': 'papertrail',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'papertrail',
        },
    },
    'loggers': {
        'gunicorn.error': {
            'handlers': ['console', 'papertrail'],
            'level': 'INFO',
            'propagate': True,
        },
        'gunicorn.access': {
            'handlers': ['console', 'papertrail'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}