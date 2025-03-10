import logging
import os
import socket
from logging.handlers import RotatingFileHandler, SysLogHandler

def configure_logging(app):
    """Configure logging for the Flask application."""
    
    try:
            
        # Ensure log directory exists
        log_dir = os.path.join(app.root_path, 'logs')
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            app.logger.warning(f"Could not create/access log directory: {e}")
            # Fall back to the app's root directory if needed
            log_dir = app.root_path
        
        # Set up file logging with rotation
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'flask_app.log'),
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        
        # Define log format for file logs (keep your custom trace_id field)
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] [%(module)s:%(lineno)d] [trace_id=%(trace_id)s] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        
        # Set up Papertrail logging via SysLogHandler
        papertrail_handler = SysLogHandler(
            address=('logs6.papertrailapp.com', 23995),
            socktype=socket.SOCK_DGRAM
        )
        
        # Use a formatter that fits the syslog standard and clearly identifies Flask logs
        papertrail_formatter = logging.Formatter(
            '%(asctime)s [FLASK] %(levelname)s [%(name)s]: %(message)s',
            datefmt='%b %d %H:%M:%S'
        )
        papertrail_handler.setFormatter(papertrail_formatter)
        papertrail_handler.setLevel(logging.INFO)
        
        # Add a trace_id filter to provide that value in the log context
        class TraceIDFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, 'trace_id'):
                    record.trace_id = 'no-trace-id'
                return True
        
        file_handler.addFilter(TraceIDFilter())
        papertrail_handler.addFilter(TraceIDFilter())
        
        # Add handlers to the app logger
        app.logger.addHandler(file_handler)
        app.logger.addHandler(papertrail_handler)
        app.logger.setLevel(logging.INFO)
        
        # Also configure the werkzeug logger (Flask's built-in server) to use the same handlers
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.handlers = []
        werkzeug_logger.addHandler(file_handler)
        werkzeug_logger.addHandler(papertrail_handler)
        werkzeug_logger.setLevel(logging.INFO)
        
        # Configure other Flask-related loggers
        for logger_name in ['flask', 'flask.app']:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
            logger.addHandler(file_handler)
            logger.addHandler(papertrail_handler)
            logger.setLevel(logging.INFO)
        
        app.logger.info('Application logging configured')
    
    except Exception as e:
        app.logger.info(f"There has been an error setting up the logging configuration: {e}")
    finally: 
        return app