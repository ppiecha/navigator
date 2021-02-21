import fnmatch
import os
from operator import itemgetter
from threading import Thread
from typing import List, Tuple, Sequence, Dict
from util import constants as cn, util_file
from util.util_type import PathItem
from pubsub import pub
import win32file
import win32event
import win32con
from pathlib import Path
import logging
from lib4py import logger as lg
import time

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)

ACTIONS = {
  1: "Created",
  2: "Deleted",
  3: "Updated",
  4: "Renamed from something",
  5: "Renamed to something"
}

FILE_LIST_DIRECTORY = 0x0001


class DirWatcher(Thread):
    def __init__(self, frame, dir_name, dir_items, file_items):
        super().__init__()
        self.frame = frame
        self.exit = False
        self.dir_name = str(dir_name)
        self.dir_items = dir_items
        self.file_items = file_items
        try:
            self.change_handle = win32file.FindFirstChangeNotification(
                                            self.dir_name,
                                            0,
                                            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                                            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES | win32con.FILE_NOTIFY_CHANGE_SIZE |
                                            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
                                            )
            self.start()
        except:
            self.terminate()

    def terminate(self):
        self.exit = True
        logger.debug(f"terminated {self.dir_name}")

    def run(self):

        def get_content(dir_name: str):
            with os.scandir(dir_name) as it:
                return [f.name for f in it]

        try:
            try:
                old_content = get_content(dir_name=self.dir_name)
            except:
                self.terminate()
                return
            while not self.exit:
                result = win32event.WaitForSingleObject(self.change_handle, 500)
                if result == win32con.WAIT_OBJECT_0:
                    if not Path(self.dir_name).exists():
                        logger.debug(f"Dir not exists {self.dir_name} exiting")
                        break
                    new_content = get_content(dir_name=self.dir_name)
                    added = [Path(os.path.join(self.dir_name, f)) for f in new_content if f not in old_content]
                    deleted = [f for f in old_content if f not in new_content]
                    self.add_remove(added, deleted)
                    old_content = new_content
                    win32file.FindNextChangeNotification(self.change_handle)
        finally:
            if hasattr(self, 'change_handle'):
                win32file.FindCloseChangeNotification(self.change_handle)

    def add_remove(self, added, deleted):
        if deleted:
            logger.debug(f"Items deleted: {deleted}")
            for item in deleted:
                path = Path(os.path.join(self.dir_name, item))
                logger.debug(f"before cash item delete {path}")
                if self.frame.dir_cache.is_in_cache(dir_name=str(path)):
                    logger.debug(f"dir deleted {str(path)}")
                    pub.sendMessage(cn.CN_TOPIC_DIR_DEL, dir_name=str(path))
                    self.frame.dir_cache.delete_cache_item(dir_name=str(path))
        self.frame.dir_cache.refresh_dir(dir_name=self.dir_name)
        pub.sendMessage(cn.CN_TOPIC_DIR_CHG, dir_name=self.dir_name, added=added, deleted=deleted)
        time.sleep(0.5)


class DirCacheItem:
    def __init__(self, frame, dir_name: str) -> None:
        if not dir_name:
            raise ValueError("Empty dir name")
        self.frame = frame
        self.dir_name: str = dir_name
        self.dir_items: List[PathItem] = []
        self.file_items: List[PathItem] = []
        self.watcher = DirWatcher(frame=frame, dir_name=dir_name, dir_items=self.dir_items,
                                  file_items=self.file_items)
        self.open_dir(dir_name)

    def open_dir(self, dir_name: str):
        self.dir_items = []
        self.file_items = []
        if not self.watcher.is_alive():
            self.watcher = DirWatcher(frame=self.frame, dir_name=dir_name, dir_items=self.dir_items,
                                      file_items=self.file_items)
        with os.scandir(dir_name) as sd:
            sd = [item for item in sd if (not self.frame.app_conf.show_hidden and not util_file.is_hidden(Path(item.path)))
                  or self.frame.app_conf.show_hidden]
            for i in sd:
                if i.is_dir():

                    self.dir_items.append(PathItem(lower_name=i.name.lower(),
                                                   date=i.stat().st_mtime,
                                                   size="",
                                                   name=i.name,
                                                   is_dir=i.is_dir(),
                                                   extension="",
                                                   path=Path(i.path)))
                else:
                    self.file_items.append(PathItem(lower_name=i.name.lower(),
                                                    date=i.stat().st_mtime,
                                                    size=i.stat().st_size,
                                                    name=i.name,
                                                    is_dir=i.is_dir(),
                                                    extension=Path(i.name).suffix,
                                                    path=Path(i.path)))


class DirCache:
    def __init__(self, frame):
        self.frame = frame
        self._dict = Dict[str, DirCacheItem]
        self._dict = {}

    def is_in_cache(self, dir_name: str) -> bool:
        return dir_name in self._dict.keys()

    def match(self, src, pat_lst):
        return len(list(filter(lambda x: fnmatch.fnmatch(src, x), pat_lst))) > 0
        # return len(list(filter(lambda x: x, map(lambda x: fnmatch.fnmatch(src, x), pat_lst)))) > 0

    def read_dir(self, dir_name: str, reread_source: bool = False) -> None:
        if not isinstance(dir_name, str):
            raise ValueError("Incorrect key type", dir_name)
        if dir_name not in self._dict.keys():
            logger.debug(f"R E A D {dir_name}")
            self._dict[dir_name] = DirCacheItem(frame=self.frame, dir_name=dir_name)
        if reread_source:
            # print("R E A D - refresh cache", dir_name)
            self._dict[dir_name].open_dir(dir_name=dir_name)

    def get_dir(self, dir_name: str, conf, reread_source: bool = False) -> Sequence:
        self.read_dir(dir_name=dir_name, reread_source=reread_source)
        pattern = conf.pattern if conf.use_pattern else ["*"]
        return sorted([d for d in self._dict[dir_name].dir_items if self.match(d[cn.CN_COL_NAME], pattern)],
                      key=itemgetter(conf.sort_key), reverse=conf.sort_desc) + \
               sorted([f for f in self._dict[dir_name].file_items if self.match(f[cn.CN_COL_NAME], pattern)],
                      key=itemgetter(conf.sort_key), reverse=conf.sort_desc)

    def refresh_dir(self, dir_name: str) -> None:
        """refresh cache for given directory"""
        if Path(dir_name).exists():
            self.read_dir(dir_name=dir_name, reread_source=True)
        else:
            self.delete_cache_item(dir_name=dir_name)

    def refresh(self) -> None:
        """refresh all the items in the cache"""
        for dir_name in self._dict.keys():
            self.refresh_dir(dir_name=dir_name)

    def release_resources(self):
        """release all cache resources"""
        for item in self._dict.keys():
            self.remove_watcher(dir=item)
        self._dict.clear()
        logger.debug("cache cleared")

    def remove_watcher(self, dir: str) -> None:
        th = self._dict[dir].watcher
        if th.is_alive():
            th.terminate()
            # th.join()

    def delete_cache_item(self, dir_name: str) -> None:
        lst = list(self._dict.keys())
        for item in lst:
            if str(item).startswith(dir_name):
                logger.debug(f"removing wather {item}")
                self.remove_watcher(item)
                del self._dict[item]
        pub.sendMessage(cn.CN_TOPIC_DIR_DEL, dir_name=dir_name)
