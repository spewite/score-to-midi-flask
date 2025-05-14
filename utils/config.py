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
        
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] [%(module)s:%(lineno)d] [trace_id=%(trace_id)s] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        
        # Set up console logging
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] [%(module)s:%(lineno)d] [trace_id=%(trace_id)s] - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
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
        
        app.logger.info('Application logging configured with file and console output.') # Updated message
    
    except Exception as e:
        import sys
        print(f"Critical error setting up logging configuration: {e}", file=sys.stderr)
    finally: 
        return app