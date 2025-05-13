import logging # Import the main logging module
import os
import socket
# Import specific handlers from logging.handlers
from logging.handlers import RotatingFileHandler, SysLogHandler
# StreamHandler is part of the core logging module, not logging.handlers

def configure_logging(app):
    """Configure logging for the Flask application."""
    
    try:
            
        # Ensure log directory exists
        log_dir = os.path.join(app.root_path, 'logs')
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            # Use a basic print here if logger is not yet configured or use app.logger if it's safe
            print(f"Warning: Could not create/access log directory: {e}")
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
            address=('logs6.papertrailapp.com', 23995), # Replace with your Papertrail address and port
            socktype=socket.SOCK_DGRAM  # Use SOCK_DGRAM for UDP
        )
        
        # Use a formatter that fits the syslog standard and clearly identifies Flask logs
        papertrail_formatter = logging.Formatter(
            '%(asctime)s [FLASK_APP_NAME] %(levelname)s [%(name)s]: %(message)s', # Consider adding your app name
            datefmt='%b %d %H:%M:%S'
        )
        papertrail_handler.setFormatter(papertrail_formatter)
        papertrail_handler.setLevel(logging.INFO)

        # Set up console logging
        console_handler = logging.StreamHandler() # Use logging.StreamHandler()
        # You can use a similar formatter or a simpler one for the console
        console_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] [trace_id=%(trace_id)s] - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO) # Or set to DEBUG for more verbose output during development
        
        # Add a trace_id filter to provide that value in the log context
        class TraceIDFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, 'trace_id'):
                    record.trace_id = 'no-trace-id' # Default if no trace_id is set
                return True
        
        # Apply the filter to all handlers
        trace_filter = TraceIDFilter()
        file_handler.addFilter(trace_filter)
        papertrail_handler.addFilter(trace_filter)
        console_handler.addFilter(trace_filter) # Add filter to console handler as well
        
        # Add handlers to the app logger
        # It's good practice to clear existing handlers if reconfiguring
        app.logger.handlers = [] 
        app.logger.addHandler(file_handler)
        app.logger.addHandler(papertrail_handler)
        app.logger.addHandler(console_handler) # Add the console handler
        app.logger.setLevel(logging.INFO) # Set the app logger level
        
        # Also configure the werkzeug logger (Flask's built-in server) to use the same handlers
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.handlers = [] # Clear existing handlers
        werkzeug_logger.addHandler(file_handler)
        werkzeug_logger.addHandler(papertrail_handler)
        werkzeug_logger.addHandler(console_handler) # Add console handler to werkzeug
        werkzeug_logger.setLevel(logging.INFO) # Or logging.ERROR in production to reduce noise
        
        # Configure other Flask-related loggers if necessary
        for logger_name in ['flask', 'flask.app']: # 'flask.app' is often the same as app.logger
            logger = logging.getLogger(logger_name)
            # Avoid double-adding if logger_name is 'flask.app' and app.logger is already configured
            if logger is not app.logger: 
                logger.handlers = []
                logger.addHandler(file_handler)
                logger.addHandler(papertrail_handler)
                logger.addHandler(console_handler)
                logger.setLevel(logging.INFO)
        
        app.logger.info('Application logging configured with file, Papertrail, and console output.')
    
    except Exception as e:
        # If logging setup fails, print to stderr as a last resort
        import sys
        print(f"Critical error setting up logging configuration: {e}", file=sys.stderr)
        # Optionally, re-raise the exception if it's fatal for the app
        # raise
    finally: 
        return app
