import os
import sys
from pathlib import Path

CN_APP_NAME = "Finder"
CN_APP_RESULTS = "Finder results"
CN_APP_PATH = os.path.dirname(os.path.abspath(__file__))

sys.path.append(str(Path(CN_APP_PATH).parent))

CN_ICON_FILE_NAME = os.path.join(CN_APP_PATH, "img\\finder.ico")

CN_IM_NEW_SEARCH = os.path.join(CN_APP_PATH, "img\\new_search.png")
CN_IM_NEW_FOLDER = os.path.join(CN_APP_PATH, "img\\new_folder.png")
CN_IM_NEW_FILE = os.path.join(CN_APP_PATH, "img\\new_file.png")
CN_IM_NEW_DOC = os.path.join(CN_APP_PATH, "img\\new_document.png")
CN_IM_STOP = os.path.join(CN_APP_PATH, "img\\stop.png")
CN_TOPIC_ADD_NODE = "ADD_NODE"
CN_TOPIC_UPDATE_STATUS = "UPDATE_STATUS"
CN_TOPIC_SEARCH_COMPLETED = "SEARCH_COMPLETED"


