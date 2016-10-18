import logging

FORMAT = "[%(asctime)s] [%(levelname)s] [%(threadName)s:%(name)s] %(msg)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
formatter = logging.Formatter(FORMAT, datefmt=DATE_FORMAT)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

def create_logger(name):
    return logging.getLogger(name)