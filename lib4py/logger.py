import logging


def get_console_logger(name: str, log_level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level=log_level)
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level=log_level)
    c_format = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    # print(name, logger.handlers)
    return logger
