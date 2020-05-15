from pathlib import Path


class BrowserConf:
    def __init__(self,
                 last_path=Path.home(),
                 path_history=[],
                 column_conf={},
                 sort_key=0,
                 sort_desc=False,
                 pattern="*",
                 use_pattern=True
                ):
        self.last_path = last_path
        self.path_history = path_history
        self.column_conf = column_conf if column_conf else {0: True, 1: True}
        self.sort_key = sort_key
        self.sort_desc = sort_desc
        self.pattern = pattern
        self.use_pattern = use_pattern

    def __str__(self):
        return str(self.last_path)


class NavigatorConf:
    def __init__(self):
        self.left_browser = BrowserConf()
        self.right_browser = BrowserConf()
        self.show_system = False
        self.show_hidden = False

    def __str__(self):
        return "Left browser: " + str(self.left_browser) + "\n" + "Right browser: " + str(self.right_browser)
