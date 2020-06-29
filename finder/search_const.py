import os


CN_APP_PATH = os.path.dirname(os.path.abspath(__file__))

CN_IM_NEW_FOLDER = os.path.join(CN_APP_PATH, "img\\new_folder.png")
CN_IM_NEW_FILE = os.path.join(CN_APP_PATH, "img\\new_file.png")
CN_IM_NEW_DOC = os.path.join(CN_APP_PATH, "img\\new_document.png")

OPT_CASE_SENSITIVE = 1
OPT_WHOLE_WORD = 2
OPT_REG_EXP = 3
OPT_NOT_CONTAINS = 4
OPT_SUB_DIRS = 5
OPT_FILE_NAMES = 6
OPT_DIRS = 7
