import threading
import webbrowser
from pathlib import Path

from lib4py import shell as sh
from lib4py import logger as lg
from typing import Callable, List, Sequence
import logging
import time
import wx

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)


def open_url(url: str, browser_path: str = "") -> None:
    if not browser_path:
        browser_path = "google-chrome"
    else:
        browser_path = Path(browser_path).as_posix() + " %s"
        logger.debug(f"Web browser path {browser_path}")
    try:
        webbrowser.get(using=browser_path).open_new_tab(url=url)
    except webbrowser.Error as e:

        webbrowser.get(using=None).open_new_tab(url=url)


def get_text_from_clip() -> str:
    clipboard = wx.Clipboard()
    data = wx.TextDataObject()
    try:
        if clipboard.Open():
            if clipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                clipboard.GetData(data)
            else:
                return ""
        else:
            return ""
    except Exception as e:
        logger.debug(str(e))
        text = ""
    else:
        text = data.GetText()
    finally:
        clipboard.Close()
    return text


def open_clip_url(browser_path: str = "") -> None:
    open_url(url=get_text_from_clip(), browser_path=browser_path)


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

