import logging
import sys

from entity.constants import LOGGER_GOQUANT
from config.config import TradingConfig


class Logger(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            # Put any initialization here.
            cls._init(cls)
        return cls._instance

    def _init(self):
        self.cfg = TradingConfig()
        self.logger = logging.getLogger(LOGGER_GOQUANT)
        if not self.logger.handlers:
            formatter = logging.Formatter('%(module)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s')

            self.logger.setLevel(self.cfg.logging_level)

            # create a file handler
            handler_file = logging.FileHandler(self.cfg.logging_file)
            handler_file.setFormatter(formatter)

            handler_stdout = logging.StreamHandler(sys.stdout)
            handler_stdout.setFormatter(formatter)

            # self.logger.addHandler(handler_stdout)
            self.logger.addHandler(handler_file)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)


logger = Logger()
