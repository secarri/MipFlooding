# Default packages
import logging


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
