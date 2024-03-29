import os

import win32con
import wx.lib.newevent
from pathlib import Path
from util.com_type import HotKey

ID_SPLITTER = wx.NewId()
ID_SQL_SPLITTER1 = wx.NewId()
ID_SQL_SPLITTER2 = wx.NewId()

CN_APP_NAME = "Navigator"
CN_APP_NAME_VIEWER = "Code navigator"
CN_SQL_NAVIGATOR = "SQL navigator"
CN_TOOL_NAME = "Assistant"
CN_CUSTOM_PATHS = "Custom paths"
CN_EXT_EDITORS = "External editors"
CN_EXT_TEXT_EDIT = "External text editor"
CN_EXT_DIFF_EDIT = "Diff editor"
CN_EXT_BROWSER = "Web browser"
CN_URLS = "URLs"
CN_URL_LEFT = "Left arrow url"
CN_URL_RIGHT = "Right arrow url"

CN_GO_BACK = ".."

CN_APP_PATH = os.path.dirname(os.path.abspath(__file__))

CN_APP_CONFIG = os.path.join(CN_APP_PATH, "../config.dat")
CN_APP_LOG = os.path.join(CN_APP_PATH, "../navigator.log")

CN_VIEWER_APP = Path(os.path.join(CN_APP_PATH, "viewer\\viewer.py"))
CN_FINDER_APP = Path(os.path.join(CN_APP_PATH, "../finder/finder.py"))

CN_ICON_FILE_NAME = os.path.join(CN_APP_PATH, "../img/navigator4.ico")
CN_ICON_CODE_VIEWER = os.path.join(CN_APP_PATH, "../img/code_viewer.ico")

# Messages
CN_NO_ITEMS_SEL = "No items selected"
CN_SEL_ONE_ITEM = "Select one item"
CN_SEL_ONE_FILE = "Select one file"

# Hot keys
ID_HOT_KEY_SHOW = wx.NewId()
ID_HOT_KEY_SHOW_CLIP = wx.NewId()
ID_HOT_KEY_CLIP_URL = wx.NewId()
ID_HOT_KEY_LEFT_URL = wx.NewId()
ID_HOT_KEY_RIGHT_URL = wx.NewId()
ID_HOT_KEY_NUMPAD_URL = {}
for key in range(9):
    ID_HOT_KEY_NUMPAD_URL[str(key + 1)] = wx.NewId()


# File
ID_NEW_FILE = wx.NewId()
ID_RENAME = wx.NewId()
ID_VIEW = wx.NewId()
ID_EDIT = wx.NewId()
ID_COPY = wx.NewId()
ID_MOVE = wx.NewId()
ID_NEW_FOLDER = wx.NewId()
ID_DELETE = wx.NewId()
ID_SEP = wx.NewId()
ID_EXIT = wx.NewId()
ID_CREATE_SHORTCUT = wx.NewId()
ID_COPY2SAME = wx.NewId()
ID_COPY_CLIP = wx.NewId()
ID_COPY_CLIP_FILE_CONTENT = wx.NewId()
ID_PASTE_CLIP = wx.NewId()
ID_PASTE_CLIP_FILE_CONTENT = wx.NewId()
# EDIT
ID_SELECT_ALL = wx.NewId()
ID_INVERT_SEL = wx.NewId()
ID_COPY_SEL_NAMES = wx.NewId()
ID_COPY_SEL_NAMES_AND_PATHS = wx.NewId()
# CMD
ID_TARGET_EQ_SRC = wx.NewId()
ID_SWAP_WIN = wx.NewId()
ID_DIFF = wx.NewId()
ID_SEARCH = wx.NewId()
ID_HISTORY = wx.NewId()
ID_CMD = wx.NewId()
# VIEW
ID_ALWAYS_ON_TOP = wx.NewId()
ID_REREAD = wx.NewId()
ID_CLEAR_CACHE = wx.NewId()
ID_SHOW_HIDDEN = wx.NewId()

MOD_KEY = win32con.MOD_WIN | win32con.MOD_ALT


class MItem:
    def __init__(self, id=None, name=None, key=None, type=wx.ITEM_NORMAL, acc_type=wx.ACCEL_NORMAL, hidden=False):
        self.id = id
        self.name = name
        self.type = type
        self.acc_type = acc_type
        self.key = key
        self.hidden = hidden


dt_hot_keys = {
    ID_HOT_KEY_SHOW:        HotKey(id=ID_HOT_KEY_SHOW, mod_key=MOD_KEY, key=win32con.VK_RETURN,
                                   action=None, url="", caption=""),
    ID_HOT_KEY_SHOW_CLIP:   HotKey(id=ID_HOT_KEY_SHOW_CLIP, mod_key=MOD_KEY, key=win32con.VK_UP,
                                   action=None, url="", caption=""),
    ID_HOT_KEY_CLIP_URL:    HotKey(id=ID_HOT_KEY_CLIP_URL, mod_key=MOD_KEY, key=win32con.VK_DOWN,
                                   action=None, url="", caption=""),
    ID_HOT_KEY_LEFT_URL:    HotKey(id=ID_HOT_KEY_LEFT_URL, mod_key=MOD_KEY, key=win32con.VK_LEFT,
                                   action=None, url="", caption=CN_URL_LEFT),
    ID_HOT_KEY_RIGHT_URL:   HotKey(id=ID_HOT_KEY_RIGHT_URL, mod_key=MOD_KEY, key=win32con.VK_RIGHT,
                                   action=None, url="", caption=CN_URL_RIGHT)
}

num_keys = [win32con.VK_NUMPAD1, win32con.VK_NUMPAD2, win32con.VK_NUMPAD3, win32con.VK_NUMPAD4, win32con.VK_NUMPAD5,
            win32con.VK_NUMPAD6, win32con.VK_NUMPAD7, win32con.VK_NUMPAD8, win32con.VK_NUMPAD9]
for ind, (key, num) in enumerate(zip(ID_HOT_KEY_NUMPAD_URL.values(), num_keys), start=1):
    dt_hot_keys[key] = HotKey(id=key, mod_key=MOD_KEY, key=num, action=None, url="", caption=f"Numpad {ind}")

dt_file = {
    ID_RENAME:          MItem(id=ID_RENAME, name="Rename", key=wx.WXK_F2),
    ID_VIEW:            MItem(id=ID_VIEW, name="View", key=wx.WXK_F3),
    ID_EDIT:            MItem(id=ID_EDIT, name="Edit", key=wx.WXK_F4),
    ID_COPY:            MItem(id=ID_COPY, name="Copy", key=wx.WXK_F5),
    ID_COPY2SAME:       MItem(id=ID_COPY2SAME, name="Copy to the same folder", key=wx.WXK_F5,
                              acc_type=wx.ACCEL_SHIFT),
    ID_CREATE_SHORTCUT: MItem(id=ID_CREATE_SHORTCUT, name="Create shortcut", key=wx.WXK_F5,
                              acc_type=wx.ACCEL_SHIFT + wx.ACCEL_CTRL),
    ID_MOVE:            MItem(id=ID_MOVE, name="Move", key=wx.WXK_F6),
    ID_NEW_FOLDER:      MItem(id=ID_NEW_FOLDER, name="New folder", key=wx.WXK_F7),
    ID_DELETE:          MItem(id=ID_DELETE, name="Delete", key=wx.WXK_F8),
    ID_NEW_FILE:        MItem(id=ID_NEW_FILE, name="New file", key=wx.WXK_F9),
    ID_SEP:             MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_EXIT:            MItem(id=ID_EXIT, name="Exit", key=wx.WXK_F4, acc_type=wx.ACCEL_ALT),
}

dt_edit = {
    ID_SELECT_ALL:                  MItem(id=ID_SELECT_ALL, name="Select all", key=ord("A"), acc_type=wx.ACCEL_CTRL),
    ID_INVERT_SEL:                  MItem(id=ID_INVERT_SEL, name="Invert selection", key=ord("A"),
                                          acc_type=wx.ACCEL_SHIFT + wx.ACCEL_CTRL),
    ID_SEP:                         MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_COPY_CLIP:                   MItem(id=ID_COPY_CLIP, name="Copy selected items to clipboard", key=ord("C"),
                                          acc_type=wx.ACCEL_CTRL, hidden=False),
    ID_PASTE_CLIP:                  MItem(id=ID_PASTE_CLIP, name="Paste items from clipboard", key=ord("V"),
                                          acc_type=wx.ACCEL_CTRL, hidden=False),
    wx.NewId():                     MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_COPY_SEL_NAMES:              MItem(id=ID_COPY_SEL_NAMES, name="Copy selected names", key=ord("C"),
                                          acc_type=wx.ACCEL_SHIFT + wx.ACCEL_CTRL),
    ID_COPY_SEL_NAMES_AND_PATHS:    MItem(id=ID_COPY_SEL_NAMES_AND_PATHS, name="Copy selected names with path",
                                          key=ord("C"), acc_type=wx.ACCEL_SHIFT),
    wx.NewId():                     MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_COPY_CLIP_FILE_CONTENT:      MItem(id=ID_COPY_CLIP_FILE_CONTENT,
                                          name="Copy file content to clipboard", key=ord("C"),
                                          acc_type=wx.ACCEL_ALT),
    ID_PASTE_CLIP_FILE_CONTENT:     MItem(id=ID_PASTE_CLIP_FILE_CONTENT,
                                          name="Paste text from clipboard to file",
                                          key=ord("V"), acc_type=wx.ACCEL_ALT),
}

dt_cmd = {
    ID_TARGET_EQ_SRC:               MItem(id=ID_TARGET_EQ_SRC, name="Target = Source", key=ord("T"),
                                          acc_type=wx.ACCEL_CTRL),
    ID_SWAP_WIN:                    MItem(id=ID_SWAP_WIN, name="Swap path in tabs", key=ord("T"),
                                          acc_type=wx.ACCEL_SHIFT + wx.ACCEL_CTRL),
    wx.NewId():                     MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_DIFF:                        MItem(id=ID_DIFF, name="Compare files (diff)", key=ord("D"),
                                          acc_type=wx.ACCEL_CTRL),
    wx.NewId():                     MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_SEARCH:                      MItem(id=ID_SEARCH, name="Search", key=ord("F"), acc_type=wx.ACCEL_CTRL),
    ID_HISTORY:                     MItem(id=ID_HISTORY, name="History",
                                          key=ord("H"), acc_type=wx.ACCEL_CTRL),
    wx.NewId():                     MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_CMD:                         MItem(id=ID_CMD, name="Run command prompt", key=ord("P"),
                                          acc_type=wx.ACCEL_CTRL)
}

dt_view = {
    ID_ALWAYS_ON_TOP:               MItem(id=ID_ALWAYS_ON_TOP, name="Always on top", key=None,
                                          acc_type=None, type=wx.ITEM_CHECK),
    wx.NewId():                     MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_REREAD:                      MItem(id=ID_REREAD, name="Reread source", key=ord("R"),
                                          acc_type=wx.ACCEL_CTRL),
    ID_CLEAR_CACHE:                 MItem(id=ID_CLEAR_CACHE, name="Clear cache"),
    wx.NewId():                     MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_SHOW_HIDDEN:                 MItem(id=ID_SHOW_HIDDEN, name="Show hidden", key=ord("H"),
                                          type=wx.ITEM_CHECK, acc_type=wx.ACCEL_CTRL)
}

CN_IM_FOLDER = os.path.join(CN_APP_PATH, "../img/folder.png")
CN_IM_FILE = os.path.join(CN_APP_PATH, "../img/file.png")
CN_IM_GO_UP = os.path.join(CN_APP_PATH, "../img/go_up.png")
CN_IM_ARROW_UP = os.path.join(CN_APP_PATH, "../img/arrow_up.png")
CN_IM_ARROW_DOWN = os.path.join(CN_APP_PATH, "../img/arrow_down.png")
CN_IM_SEARCH = os.path.join(CN_APP_PATH, "../img/search.png")
CN_IM_FILTER = os.path.join(CN_APP_PATH, "../img/filter.png")
CN_IM_FILTER_OFF = os.path.join(CN_APP_PATH, "../img/filter_off.png")
CN_IM_FAV = os.path.join(CN_APP_PATH, "../img/star.png")
CN_IM_HIST = os.path.join(CN_APP_PATH, "../img/hist.png")
CN_IM_OK = os.path.join(CN_APP_PATH, "../img/ok.png")
CN_IM_ADD = os.path.join(CN_APP_PATH, "../img/add.png")
CN_IM_EDIT = os.path.join(CN_APP_PATH, "../img/edit.png")
CN_IM_REMOVE = os.path.join(CN_APP_PATH, "../img/remove.png")
CN_IM_HARD_DISK = os.path.join(CN_APP_PATH, "../img/hard_disk.png")
CN_IM_TOOLS = os.path.join(CN_APP_PATH, "../img/gear_wheel.png")
CN_IM_ANCHOR = os.path.join(CN_APP_PATH, "../img/anchor.png")
CN_IM_HOME = os.path.join(CN_APP_PATH, "../img/home.png")
CN_IM_USER = os.path.join(CN_APP_PATH, "../img/user.png")
CN_IM_PARENT = os.path.join(CN_APP_PATH, "../img/parent.png")
CN_IM_CHILD = os.path.join(CN_APP_PATH, "../img/child.png")
CN_IM_NEW_FOLDER = os.path.join(CN_APP_PATH, "../img/new_folder.png")
CN_IM_NEW_FILE = os.path.join(CN_APP_PATH, "../img/new_file.png")
CN_IM_LINK = os.path.join(CN_APP_PATH, "../img/link.png")
CN_IM_SHORTCUT = os.path.join(CN_APP_PATH, "../img/shortcut.png")
# CN_IM_DELETE = os.path.join(CN_APP_PATH, "img\\delete.png")
# CN_IM_NEW_FILE = os.path.join(CN_APP_PATH, "img\\new_file.png")
# CN_IM_EDITOR = os.path.join(CN_APP_PATH, "img\\editor.png")
CN_IM_SEARCH_DOWN = os.path.join(CN_APP_PATH, "../img/search_down.png")
CN_IM_SEARCH_UP = os.path.join(CN_APP_PATH, "../img/search_up.png")
CN_IM_CLOSE = os.path.join(CN_APP_PATH, "../img/delete.png")
CN_IM_WORD = os.path.join(CN_APP_PATH, "../img/word.png")
CN_IM_WORD_OFF = os.path.join(CN_APP_PATH, "../img/word_off.png")
CN_IM_CASE = os.path.join(CN_APP_PATH, "../img/case.png")
CN_IM_CASE_OFF = os.path.join(CN_APP_PATH, "../img/case_off.png")

CN_COL_LNAME = 0
CN_COL_DATE = 1
CN_COL_SIZE = 2
CN_COL_NAME = 3
CN_COL_ISDIR = 4
CN_COL_EXT = 5
CN_COL_FULL_PATH = 6

CN_TOPIC_DIR_CHG = "DIR_CHANGED"
CN_TOPIC_DIR_DEL = "DIR_DELETED"
CN_TOPIC_REREAD = "REREAD"








