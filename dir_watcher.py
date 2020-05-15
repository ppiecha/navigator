import os
from threading import Thread


import win32file
import win32event
import win32con
from pathlib import Path


class DirWatcher(Thread):
    def __init__(self, path, browser):
        super().__init__()
        self.exit = False
        self.path = str(path)
        self.browser = browser
        try:
            self.change_handle = win32file.FindFirstChangeNotification (
                                            str(path),
                                            0,
                                            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME
                                            )
        except:
            self.terminate()

    def terminate(self):
        self.exit = True

    def run(self):
        try:
            try:
                old_path_contents = os.listdir(self.path)
            except:
                self.terminate()
            while not self.exit:
                result = win32event.WaitForSingleObject(self.change_handle, 500)
                if result == win32con.WAIT_OBJECT_0:
                    new_path_contents = os.listdir(self.path)
                    added = [Path(os.path.join(self.path, f)) for f in new_path_contents if f not in old_path_contents]
                    deleted = [f for f in old_path_contents if f not in new_path_contents]
                    self.browser.add_remove(added, deleted)
                    old_path_contents = new_path_contents
                    win32file.FindNextChangeNotification(self.change_handle)
        finally:
            if hasattr(self, 'change_handle'):
                win32file.FindCloseChangeNotification(self.change_handle)
