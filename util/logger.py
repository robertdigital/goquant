import logging

from config.config import TradingConfig

class Logger(object):
    def __init__(self):
        self.cfg = TradingConfig()
        self.logger = logging.getLogger("goquant")
        logging.basicConfig()
        logging.getLogger().setLevel(self.cfg.logging_level)

        logging_file = None
        # create a file handler
        if logging_file is None:
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(logging_file)

        formatter = logging.Formatter('%(module)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)


logger = Logger()
