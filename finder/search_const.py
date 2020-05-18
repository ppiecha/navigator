import os


CN_APP_PATH = os.path.dirname(os.path.abspath(__file__))

CN_IM_FOLDERS = os.path.join(CN_APP_PATH, "img\\folders.png")
CN_IM_FILES = os.path.join(CN_APP_PATH, "img\\files.png")

OPT_CASE_SENSITIVE = 1
OPT_WHOLE_WORD = 2
OPT_REG_EXP = 3
OPT_NOT_CONTAINS = 4
OPT_SUB_DIRS = 5
OPT_FILE_NAMES = 6