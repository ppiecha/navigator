import os
import sys
import wx
from pathlib import Path

CN_APP_NAME = "Drive navigator"
CN_APP_RESULTS = "Drive navigator results"
CN_APP_PATH = os.path.dirname(os.path.abspath(__file__))

sys.path.append(str(Path(CN_APP_PATH).parent))

CN_ICON_FILE_NAME = os.path.join(CN_APP_PATH, "img\\finder.ico")

CN_IM_SEARCH = os.path.join(CN_APP_PATH, "img\\search.png")
CN_IM_EXPAND = os.path.join(CN_APP_PATH, "img\\expand.png")
CN_IM_COLLAPSE = os.path.join(CN_APP_PATH, "img\\collapse.png")
CN_IM_FOLDER = os.path.join(CN_APP_PATH, "img\\folder.png")
CN_IM_FILE = os.path.join(CN_APP_PATH, "img\\file.png")
CN_IM_DOC = os.path.join(CN_APP_PATH, "img\\document.png")
CN_IM_STOP = os.path.join(CN_APP_PATH, "img\\stop.png")
CN_IM_NAV = os.path.join(CN_APP_PATH, "img\\navigator.png")
CN_IM_VIEW = os.path.join(CN_APP_PATH, "img\\code_viewer.png")
CN_IM_SAVE = os.path.join(CN_APP_PATH, "img\\save.png")
CN_IM_CLIP = os.path.join(CN_APP_PATH, "img\\clipboard.png")
CN_TOPIC_ADD_NODE = "ADD_NODE"
CN_TOPIC_UPDATE_STATUS = "UPDATE_STATUS"
CN_TOPIC_SEARCH_NODE_COMPLETED = "SEARCH_NODE_COMPLETED"
CN_TOPIC_SEARCH_COMPLETED = "SEARCH_COMPLETED"


def get_splitter(parent):
    return wx.StaticLine(parent, size=(1, 20), style=wx.LI_VERTICAL)


