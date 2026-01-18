"""
Logging configuration for the Workout Coach application.
Provides structured logging for debugging and monitoring.
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime


def setup_logging(app_name: str = 'workoutcoach', log_level: str = None):
    """
    Set up structured logging for the application.

    Args:
        app_name: Name of the application for the logger
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)
    """
    # Determine log level from environment or parameter
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')

    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (if LOG_DIR is set)
    log_dir = os.getenv('LOG_DIR')
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'{app_name}.log')

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = None):
    """
    Get a logger instance.

    Args:
        name: Optional sub-logger name (e.g., 'strava', 'api')

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f'workoutcoach.{name}')
    return logging.getLogger('workoutcoach')


# Initialize default logger on import
logger = setup_logging()


# Convenience functions for common log patterns
def log_api_request(method: str, path: str, user_id: int = None):
    """Log an incoming API request"""
    logger = get_logger('api')
    logger.info(f"[REQUEST] {method} {path} | user_id={user_id}")


def log_api_response(method: str, path: str, status_code: int, duration_ms: float = None):
    """Log an API response"""
    logger = get_logger('api')
    duration_str = f" | {duration_ms:.1f}ms" if duration_ms else ""
    logger.info(f"[RESPONSE] {method} {path} | status={status_code}{duration_str}")


def log_db_operation(operation: str, table: str, record_id: str = None, success: bool = True):
    """Log a database operation"""
    logger = get_logger('db')
    status = "OK" if success else "FAILED"
    id_str = f" | id={record_id}" if record_id else ""
    logger.debug(f"[{status}] {operation} {table}{id_str}")


def log_strava_operation(operation: str, details: str = None, success: bool = True):
    """Log a Strava-related operation"""
    logger = get_logger('strava')
    status = "OK" if success else "FAILED"
    details_str = f" | {details}" if details else ""
    logger.info(f"[{status}] {operation}{details_str}")


def log_error(message: str, exception: Exception = None, context: dict = None):
    """Log an error with optional exception and context"""
    logger = get_logger('error')
    if exception:
        logger.error(f"{message} | exception={type(exception).__name__}: {str(exception)}")
        if context:
            logger.debug(f"Context: {context}")
    else:
        logger.error(message)
