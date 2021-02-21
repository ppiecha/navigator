from lib4py import shell as sh
from lib4py import logger as lg
from typing import Callable, List, Sequence
import logging
import time

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)


def run_in_thread(target: Callable, args: Sequence, lst: List[sh.ShellThread] = None) -> None:
    th = sh.ShellThread(target=target, args=args)
    th.start()
    if lst is not None:
        lst.append(th)


class Tit:
    def __init__(self, text):
        logger.debug(text)
        self.text = text
        self.start = time.time()

    def __del__(self):
        logger.debug(f"({self.text}) elapsed: {time.time() - self.start}")
