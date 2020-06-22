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
        self.column_conf = column_conf if column_conf else {0: True, 1: False}
        self.sort_key = sort_key
        self.sort_desc = sort_desc
        self.pattern = pattern
        self.use_pattern = use_pattern
        self.locked = locked
        self.tab_name = tab_name
        self.tab_path = tab_path

    @property
    def last_path(self):
        return self.tab_path if self.locked else self._last_path

    @last_path.setter
    def last_path(self, value):
        if not self.locked:
            self.tab_name = self.generate_tab_name(full_name=value)
        self._last_path = value

    def generate_tab_name(self, full_name, locked=False):
        item = Path(full_name)
        new_name = ""
        if item.samefile(item.anchor):
            new_name = str(item.anchor)
        else:
            new_name = self.get_short(item.name)
        return self.get_short("*" + new_name) if locked else new_name

    def lock_tab(self, user_tab_name):
        self.locked = True
        self.tab_name = "*" + user_tab_name if user_tab_name else self.generate_tab_name(full_name=self._last_path,
                                                                                         locked=True)
        self.tab_path = self._last_path

    def unlock_tab(self):
        self.locked = False
        self.tab_name = self.generate_tab_name(full_name=self._last_path, locked=False)

    def __str__(self):
        return str(self.last_path)

    def get_short(self, name):
        return name if len(name) <= 10 else name[:10] + "..."


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
        self.custom_paths = []

    def __str__(self):
        return "Left browser: " + str(self.left_browser) + "\n" + "Right browser: " + str(self.right_browser)
