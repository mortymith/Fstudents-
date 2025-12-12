import logging

# Create named loggers for different modules
db_logger = logging.getLogger("DB:")
db_logger.setLevel(level=logging.DEBUG)


__all__ = [db_logger]
