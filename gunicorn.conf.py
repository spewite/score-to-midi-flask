import logging
# SysLogHandler and socket are no longer needed here
# from logging.handlers import SysLogHandler 
# import socket

# Basic Gunicorn configuration
timeout = 300
bind = "0.0.0.0:5000"
workers = 3
worker_class = "sync"
loglevel = "info"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}

# Configure logs to go to stdout/stderr for console output
accesslog = "-"  # Send access log to stdout
errorlog = "-"   # Send error log to stderr
access_log_format = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
capture_output = True # Keep True to capture print() statements from Flask

# Simplified logconfig_dict for console output
logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False, # Set to False to not disable other loggers like Flask's
    'formatters': {
        'console_formatter': { # Renamed for clarity
            'format': '%(asctime)s [GUNICORN] %(levelname)s [%(process)d]: %(message)s',
            'datefmt': '%b %d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console_formatter', # Use the renamed formatter
            'stream': 'ext://sys.stdout' # Explicitly set to stdout
        },
    },
    'loggers': {
        'gunicorn.error': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False, # Set to False if you don't want Gunicorn error logs to propagate to root logger
        },
        'gunicorn.access': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False, # Set to False for access logs as well
        },
    },
    # Optional: Configure root logger to also use console if needed
    # 'root': {
    # 'handlers': ['console'],
    # 'level': 'INFO',
    # },
}