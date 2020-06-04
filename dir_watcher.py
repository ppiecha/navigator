import os
import wx
from threading import Thread
import constants as cn
from pubsub import pub
import win32file
import win32event
import win32con
from pathlib import Path

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
        # self.change_handle = None
        try:
            # win32file.ReadDirectoryChangesW
            # hDir = win32file.CreateFile(
            #     self.dir_name,
            #     FILE_LIST_DIRECTORY,
            #     win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            #     None,
            #     win32con.OPEN_EXISTING,
            #     win32con.FILE_FLAG_BACKUP_SEMANTICS,
            #     None
            # )
            self.change_handle = win32file.FindFirstChangeNotification(
                                            self.dir_name,
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
            try:
                index = [x[cn.CN_COL_NAME] for x in self.dir_items].index(item)
                del self.dir_items[index]
            except ValueError as e:
                pass
            try:
                index = [x[cn.CN_COL_NAME] for x in self.file_items].index(item)
                del self.file_items[index]
            except ValueError as e:
                pass

        for item in added:
            new_one = [item.name.lower(),
                       item.stat().st_mtime,
                       item.stat().st_size if item.is_file() else "",
                       item.name,
                       item.is_dir(),
                       item.suffix]
            if item.is_dir():
                self.dir_items.append(new_one)
            else:
                self.file_items.append(new_one)

        # print(added, deleted, self.dir_items)
        # Create the event
        # evt = cn.DirChangedCommandEvent(cn.ID_CMD1, dir_name="dir from thread", added=added, deleted=deleted)
        # Post the event
        # wx.CallAfter(wx.PostEvent, self.frame, evt)
        added = [item.name for item in added]
        pub.sendMessage(cn.CN_TOPIC_DIR_CHG, dir_name=Path(self.dir_name), added=added, deleted=deleted)
