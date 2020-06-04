from pathlib import Path


class BrowserConf:
    def __init__(self,
                 last_path=Path.home(),
                 path_history=[],
                 column_conf={},
                 sort_key=0,
                 sort_desc=False,
                 pattern="*",
                 use_pattern=True,
                 locked=False,
                 tab_name="",
                 tab_path=""):
        self._last_path = last_path
        self.path_history = path_history
        self.column_conf = column_conf if column_conf else {0: True, 1: True}
        self.sort_key = sort_key
        self.sort_desc = sort_desc
        self.pattern = pattern
        self.use_pattern = use_pattern
        self.locked = locked
        self.tab_name = tab_name
        self.tab_path = tab_path

    @property
    def last_path(self):
        return self._last_path

    @last_path.setter
    def last_path(self, value):
        if not self.locked:
            self.tab_name = self.generate_tab_name(full_name=value)
        self._last_path = value

    def generate_tab_name(self, full_name):
        item = Path(full_name)
        if item.samefile(item.anchor):
            return str(item.anchor[0]).lower()
        else:
            return item.name if len(item.name) <= 10 else item.name[:10] + "..."

    def lock_tab(self, user_tab_name):
        self.locked = True
        self.tab_name = user_tab_name
        self.tab_path = self._last_path

    def __str__(self):
        return str(self.last_path)


class NavigatorConf:
    def __init__(self):
        self.left_browser = []
        self.right_browser = []
        self.show_system = False
        self.show_hidden = False
        self.pos = None
        self.size = None
        self.history_limit = 20
        self.left_active_tab = None
        self.right_active_tab = None

    def __str__(self):
        return "Left browser: " + str(self.left_browser) + "\n" + "Right browser: " + str(self.right_browser)
