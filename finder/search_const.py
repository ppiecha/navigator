import os
import sys
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
CN_TOPIC_ADD_NODE = "ADD_NODE"
CN_TOPIC_UPDATE_STATUS = "UPDATE_STATUS"
CN_TOPIC_SEARCH_COMPLETED = "SEARCH_COMPLETED"


