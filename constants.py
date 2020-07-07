import os
import wx.lib.newevent
from pathlib import Path



ID_SPLITTER = wx.NewId()
# ID_CMD1 = wx.NewIdRef()
# DirChangedEvent, EVT_DIR_CHANGED_EVENT = wx.lib.newevent.NewEvent()
# DirChangedCommandEvent, EVT_DIR_CHANGED_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()

CN_APP_NAME = "Navigator"
CN_TOOL_NAME = "Assistant"

CN_GO_BACK = ".."

CN_APP_PATH = os.path.dirname(os.path.abspath(__file__))

CN_APP_CONFIG = os.path.join(CN_APP_PATH, "config.dat")
CN_APP_LOG = os.path.join(CN_APP_PATH, "navigator.log")

CN_VIEWER_APP = Path(os.path.join(CN_APP_PATH, "viewer\\viewer.py"))
CN_FINDER_APP = Path(os.path.join(CN_APP_PATH, "finder\\finder.py"))

CN_ICON_FILE_NAME = os.path.join(CN_APP_PATH, "img\\navigator.ico")

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
ID_PASTE_CLIP = wx.NewId()
# EDIT
ID_SELECT_ALL = wx.NewId()
ID_INVERT_SEL = wx.NewId()
ID_COPY_SEL_NAMES = wx.NewId()
ID_COPY_SEL_NAMES_AND_PATHS = wx.NewId()
# CMD
ID_TARGET_EQ_SRC = wx.NewId()
ID_SWAP_WIN = wx.NewId()
ID_SEARCH = wx.NewId()


class MItem:
    def __init__(self, id=None, name=None, key=None, type=wx.ITEM_NORMAL, acc_type=wx.ACCEL_NORMAL, hidden=False):
        self.id = id
        self.name = name
        self.type = type
        self.acc_type = acc_type
        self.key = key
        self.hidden = hidden


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
}

dt_cmd = {
    ID_TARGET_EQ_SRC:               MItem(id=ID_TARGET_EQ_SRC, name="Target = Source", key=ord("T"),
                                          acc_type=wx.ACCEL_CTRL),
    ID_SWAP_WIN:                    MItem(id=ID_SWAP_WIN, name="Swap path in tabs", key=ord("T"),
                                          acc_type=wx.ACCEL_SHIFT + wx.ACCEL_CTRL),
    wx.NewId():                     MItem(id=ID_SEP, name="-", type=wx.ITEM_SEPARATOR),
    ID_SEARCH:                      MItem(id=ID_SEARCH, name="Search", key=ord("F"),
                                          acc_type=wx.ACCEL_CTRL)
}


CN_IM_FOLDER = os.path.join(CN_APP_PATH, "img\\folder.png")
CN_IM_FILE = os.path.join(CN_APP_PATH, "img\\file.png")
CN_IM_GO_UP = os.path.join(CN_APP_PATH, "img\\go_up.png")
CN_IM_ARROW_UP = os.path.join(CN_APP_PATH, "img\\arrow_up.png")
CN_IM_ARROW_DOWN = os.path.join(CN_APP_PATH, "img\\arrow_down.png")
CN_IM_SEARCH = os.path.join(CN_APP_PATH, "img\\search.png")
CN_IM_FILTER = os.path.join(CN_APP_PATH, "img\\filter.png")
CN_IM_FILTER_OFF = os.path.join(CN_APP_PATH, "img\\filter_off.png")
CN_IM_FAV = os.path.join(CN_APP_PATH, "img\\star.png")
CN_IM_HIST = os.path.join(CN_APP_PATH, "img\\hist.png")
CN_IM_OK = os.path.join(CN_APP_PATH, "img\\ok.png")
CN_IM_ADD = os.path.join(CN_APP_PATH, "img\\add.png")
CN_IM_EDIT = os.path.join(CN_APP_PATH, "img\\edit.png")
CN_IM_REMOVE = os.path.join(CN_APP_PATH, "img\\remove.png")
CN_IM_HARD_DISK = os.path.join(CN_APP_PATH, "img\\hard_disk.png")
CN_IM_TOOLS = os.path.join(CN_APP_PATH, "img\\gear_wheel.png")
CN_IM_ANCHOR = os.path.join(CN_APP_PATH, "img\\anchor.png")
CN_IM_HOME = os.path.join(CN_APP_PATH, "img\\home.png")
CN_IM_USER = os.path.join(CN_APP_PATH, "img\\user.png")
CN_IM_PARENT = os.path.join(CN_APP_PATH, "img\\parent.png")
CN_IM_CHILD = os.path.join(CN_APP_PATH, "img\\child.png")
CN_IM_NEW_FOLDER = os.path.join(CN_APP_PATH, "img\\new_folder.png")
CN_IM_NEW_FILE = os.path.join(CN_APP_PATH, "img\\new_file.png")
CN_IM_NEW_HLINK = os.path.join(CN_APP_PATH, "img\\new_link.png")
CN_IM_NEW_SHORTCUT = os.path.join(CN_APP_PATH, "img\\new_shortcut.png")
# CN_IM_DELETE = os.path.join(CN_APP_PATH, "img\\delete.png")
# CN_IM_NEW_FILE = os.path.join(CN_APP_PATH, "img\\new_file.png")
# CN_IM_EDITOR = os.path.join(CN_APP_PATH, "img\\editor.png")

CN_COL_LNAME = 0
CN_COL_DATE = 1
CN_COL_SIZE = 2
CN_COL_NAME = 3
CN_COL_ISDIR = 4
CN_COL_EXT = 5

CN_TOPIC_DIR_CHG = "DIR_CHANGED"

def q(text):
    return '"' + str(text) + '"'




