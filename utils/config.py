import logging
import os
import socket # socket is no longer strictly needed here after removing SysLogHandler for Papertrail
from logging.handlers import RotatingFileHandler
# StreamHandler is part of the core logging module

def configure_logging(app):
    """Configure logging for the Flask application."""
    
    try:
        # Ensure log directory exists
        log_dir = os.path.join(app.root_path, 'logs')
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create/access log directory: {e}")
            log_dir = app.root_path
        
        # Set up file logging with rotation
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'flask_app.log'),
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        
        # Set up console logging (with color if possible)
        try:
            import colorlog
            color_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(levelname)s:%(reset)s %(message)s',
                log_colors={
                    'DEBUG': 'blue',
                    'INFO': 'cyan',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red',
                }
            )
            console_handler = colorlog.StreamHandler()
            console_handler.setFormatter(color_formatter)
        except ImportError:
            console_handler = logging.StreamHandler()
            simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(simple_formatter)

        # File handler: simple format, no color
        file_formatter = logging.Formatter('%(levelname)s: %(message)s')
        file_handler.setFormatter(file_formatter)

        file_handler.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)
        
        class TraceIDFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, 'trace_id'):
                    record.trace_id = 'no-trace-id'
                return True
        
        trace_filter = TraceIDFilter()
        file_handler.addFilter(trace_filter)
        console_handler.addFilter(trace_filter)
        
        app.logger.handlers = [] 
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.addFilter(TraceIDFilter())
        app.logger.propagate = False
        
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.handlers = []
        werkzeug_logger.addHandler(file_handler)
        werkzeug_logger.addHandler(console_handler)
        werkzeug_logger.setLevel(logging.INFO)
        
        for logger_name in ['flask', 'flask.app']:
            logger = logging.getLogger(logger_name)
            if logger is not app.logger: 
                logger.handlers = []
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)
                logger.setLevel(logging.INFO)
            logger.propagate = False
        
    except Exception as e:
        import sys
        print(f"Critical error setting up logging configuration: {e}", file=sys.stderr)
    finally: 
        return app