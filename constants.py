import os
import wx.lib.newevent
from pathlib import Path

ID_SPLITTER = wx.NewId()
# ID_CMD1 = wx.NewIdRef()
# DirChangedEvent, EVT_DIR_CHANGED_EVENT = wx.lib.newevent.NewEvent()
# DirChangedCommandEvent, EVT_DIR_CHANGED_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()

CN_APP_NAME = "Navigator"

CN_GO_BACK = ".."

CN_APP_PATH = os.path.dirname(os.path.abspath(__file__))

CN_APP_CONFIG = os.path.join(CN_APP_PATH, "config.dat")

CN_VIEWER_APP = Path(os.path.join(CN_APP_PATH, "viewer\\viewer.py"))

CN_ICON_FILE_NAME = os.path.join(CN_APP_PATH, "img\\navigator.ico")

CN_IM_FOLDER = os.path.join(CN_APP_PATH, "img\\folder.png")
CN_IM_FILE = os.path.join(CN_APP_PATH, "img\\file.png")
CN_IM_GO_UP = os.path.join(CN_APP_PATH, "img\\go_up.png")
CN_IM_ARROW_UP = os.path.join(CN_APP_PATH, "img\\arrow_up.png")
CN_IM_ARROW_DOWN = os.path.join(CN_APP_PATH, "img\\arrow_down.png")
CN_IM_SEARCH = os.path.join(CN_APP_PATH, "img\\search.png")
CN_IM_FILTER = os.path.join(CN_APP_PATH, "img\\filter.png")
CN_IM_FILTER_OFF = os.path.join(CN_APP_PATH, "img\\filter_off.png")
# CN_IM_DRIVE = os.path.join(CN_APP_PATH, "img\\drive.png")
# CN_IM_STAR = os.path.join(CN_APP_PATH, "img\\star.png")
# CN_IM_CODE = os.path.join(CN_APP_PATH, "img\\code.png")
CN_IM_FAV = os.path.join(CN_APP_PATH, "img\\fav.png")
CN_IM_HIST = os.path.join(CN_APP_PATH, "img\\hist.png")
CN_IM_OK = os.path.join(CN_APP_PATH, "img\\ok.png")
# CN_IM_RENAME = os.path.join(CN_APP_PATH, "img\\rename.png")
# CN_IM_VIEWER = os.path.join(CN_APP_PATH, "img\\viewer.png")
# CN_IM_EDIT = os.path.join(CN_APP_PATH, "img\\edit.png")
# CN_IM_COPY = os.path.join(CN_APP_PATH, "img\\copy.png")
# CN_IM_MOVE = os.path.join(CN_APP_PATH, "img\\move.png")
# CN_IM_NEW_FOLDER = os.path.join(CN_APP_PATH, "img\\new_folder.png")
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