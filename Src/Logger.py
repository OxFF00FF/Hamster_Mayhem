from Src.Colors import *
import logging


def set_logger():
    formatter = logging.Formatter(f"{WHITE}%(asctime)s - %(name)s - %(levelname)s |  %(message)s  | %(filename)s - %(funcName)s() - %(lineno)d{WHITE}")
    logging.basicConfig(format=formatter._fmt, level=logging.ERROR)

    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.ERROR)
    sqlalchemy_logger.propagate = False

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    sqlalchemy_logger.handlers = []
    sqlalchemy_logger.addHandler(handler)
