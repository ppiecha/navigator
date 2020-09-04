from datetime import datetime
import stat
import os
from lib4py import shell as sh
from typing import Callable, List, Sequence
from pathlib import Path


def run_in_thread(target: Callable, args: Sequence, lst: List[sh.ShellThread] = None) -> None:
    th = sh.ShellThread(target=target, args=args)
    th.start()
    if lst is not None:
        lst.append(th)


def format_date(timestamp, format="%Y-%m-%d %H:%M"):
    d = datetime.fromtimestamp(timestamp)
    return d.strftime(format)


def format_size(size):
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Y', suffix)

    return sizeof_fmt(size) if size != "" else ""


def is_hidden(x: Path) -> bool:
    attribute = x.stat().st_file_attributes
    path, fname = os.path.split(str(x))
    return bool(attribute & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM)) or str(fname).startswith(".")



