import os
from threading import Thread
import util


import win32file
import win32event
import win32con
from pathlib import Path


class DirWatcher(Thread):
    def __init__(self, dir_name, dir_items, file_items):
        super().__init__()
        self.exit = False
        self.dir_name = str(dir_name)
        self.dir_items = dir_items
        self.file_items = file_items
        try:
            self.change_handle = win32file.FindFirstChangeNotification(
                                            dir_name,
                                            0,
                                            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME
                                            )
            self.start()
        except:
            self.terminate()

    def terminate(self):
        self.exit = True

    def run(self):
        try:
            try:
                old_content = [f.name for f in os.scandir(self.dir_name)]
            except:
                self.terminate()
                return
            while not self.exit:
                result = win32event.WaitForSingleObject(self.change_handle, 500)
                if result == win32con.WAIT_OBJECT_0:
                    new_content = [f.name for f in os.scandir(self.dir_name)]
                    added = [Path(os.path.join(self.dir_name, f)) for f in new_content if f not in old_content]
                    deleted = [f for f in old_content if f not in new_content]
                    self.add_remove(added, deleted)
                    old_content = new_content
                    win32file.FindNextChangeNotification(self.change_handle)
        finally:
            if hasattr(self, 'change_handle'):
                win32file.FindCloseChangeNotification(self.change_handle)

    def add_remove(self, added, deleted):
        for item in deleted:
            for d in self.dir_items:
                if item == d[3]:
                    self.dir_items.remove(item)
            for f in self.file_items:
                if item == f[3]:
                    self.file_items.remove(item)

        for item in added:
            new_one = [item.name.lower(),
                       item.stat().st_mtime,
                       item.stat().st_size if item.is_file() else "",
                       item.name]
            if item.is_dir():
                self.dir_items.append(new_one)
            else:
                self.file_items.append(new_one)
            # reload list
