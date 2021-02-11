from datetime import datetime
import stat
import os
from lib4py import shell as sh
from lib4py import logger as lg
from typing import Callable, List, Sequence
from pathlib import Path
import logging
import time

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)


def run_in_thread(target: Callable, args: Sequence, lst: List[sh.ShellThread] = None) -> None:
    th = sh.ShellThread(target=target, args=args)
    th.start()
    if lst is not None:
        lst.append(th)


def format_date(timestamp, format="%Y-%m-%d %H:%M"):
    if not timestamp:
        return ""
    d = datetime.fromtimestamp(timestamp)
    return d.strftime(format)


def format_size(size):
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Y', suffix)

    if not size:
        return ""
    return sizeof_fmt(size) if size != "" else ""


def is_hidden(x: Path) -> bool:
    if not x.exists():
        return True
    try:
        attribute = x.stat().st_file_attributes
    except:
        print("Cannot get attr for", str(x))
        return True
    path, fname = os.path.split(str(x))
    ext = x.suffix
    is_temp_file: bool = False
    if ext:
        is_temp_file = ext.startswith(".~")
        if is_temp_file:
            print("temp file", ext)
    return bool(attribute & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM)) or str(fname).startswith(
        ".") or is_temp_file


class Tit:
    def __init__(self, text):
        logger.debug(text)
        self.text = text
        self.start = time.time()

    def __del__(self):
        logger.debug(f"({self.text}) elapsed: {time.time() - self.start}")
