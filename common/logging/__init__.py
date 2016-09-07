import logging

FORMAT = "[%(asctime)s] [%(levelname)s] [%(threadName)s:%(filename)s:%(funcName)s:%(lineno)d] %(msg)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
formatter = logging.Formatter(FORMAT, datefmt=DATE_FORMAT)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def get_logger(obj=None, level=None):
    if obj is not None:
        new_logger = logging.getLogger(obj.__module__ + "." + obj.__class__.__name__)
    else:
        new_logger = logging.getLogger()
    if level is not None:
        new_logger.setLevel(level)
    return new_logger
