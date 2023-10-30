# Default packages
import time
import logging
from functools import wraps


def log_execution_time(func):
    """Decorator to log the execution time of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = kwargs.get('logger')
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"- Elapsed time of '{func.__name__}': {execution_time:.2f} seconds.")
        return result
    return wrapper


def setup_logger(logger_name: str, abs_log_path: str) -> logging.Logger:
    """Set up a logger with the specified name and log to the given absolute path, returning the logger instance."""
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        handler = logging.FileHandler(abs_log_path)
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    return logger


def terminate_loggers(logger: logging.Logger) -> None:
    """Terminate and close all handlers associated with the given logger, releasing any associated resources."""
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
