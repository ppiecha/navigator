from pathlib import Path
import util
import datetime as dt
from typing import Dict, Sequence


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
        self.show_hidden = False
        self.text_editor = ""
        self.diff_editor = ""
        self.pos = None
        self.size = None
        self.history_limit = 15
        self.hist_retention_days = 30
        self.left_active_tab = None
        self.right_active_tab = None
        self.custom_paths = []
        self.search_history = []
        self.search_hist_limit = 100
        self.folder_hist = Dict[str, FolderHistItem]
        self.folder_hist = {}
        self.file_hist = Dict[str, FolderHistItem]
        self.file_hist = {}

    def __str__(self):
        return "Left browser: " + str(self.left_browser) + "\n" + "Right browser: " + str(self.right_browser)

    def add_search_hist_item(self, item):
        if not [h for h in self.search_history if h.startswith(item)]:
            self.search_history.insert(0, item)
            print("Added search hist", item)
        util.run_in_thread(self.trim_hist, [self.search_history])

    def trim_hist(self, hist):
        # to_delete = list(filter(lambda x:
        #                         len(list(filter(lambda y:
        # len([z for z in y.split(";") if z.strip() and z.startswith(x) and len(x) < len(z)]) > 0, hist))) > 0, hist))
        while len(self.search_history) > self.search_hist_limit:
            self.search_history.pop()

    def folder_hist_update_item(self, folder_name: str, date: dt.datetime) -> None:
        if folder_name in self.folder_hist.keys():
            self.folder_hist[folder_name].visited_cnt += 1
            self.folder_hist[folder_name].last_visited = date
        else:
            self.folder_hist[folder_name] = FolderHistItem(folder_name=folder_name, last_visited=date)

    def folder_hist_calc_rating(self):
        to_delete = []
        for k in self.folder_hist.keys():
            if not Path(k).exists() or (
                    dt.datetime.today() - self.folder_hist[k].last_visited).days > self.hist_retention_days:
                to_delete.append(k)
                continue
            self.folder_hist[k].calc_rating()
        self.folder_hist = {k: v for k, v in self.folder_hist.items() if k not in to_delete}
        dct = {k: v for k, v in sorted(self.folder_hist.items(), key=lambda item: item[1].rating, reverse=True)}
        return {k: dct[k] for k in list(dct)[:self.history_limit]}

    def file_hist_update_item(self, file_name: str, date: dt.datetime) -> None:
        if file_name in self.file_hist.keys():
            self.file_hist[file_name].visited_cnt += 1
            self.file_hist[file_name].last_visited = date
        else:
            self.file_hist[file_name] = FileHistItem(folder_name=file_name, last_visited=date)

    def file_hist_calc_rating(self):
        for fn in self.file_hist.keys():
            self.file_hist[fn].calc_rating()
        dct = {k: v for k, v in sorted(self.file_hist.items(), key=lambda item: item[1].rating, reverse=True)}
        return {k: dct[k] for k in list(dct)[:self.history_limit]}


class FileHistItem:
    def __init__(self, folder_name: str, last_visited: dt.datetime) -> None:
        self.file_name = folder_name
        self.last_visited = last_visited
        self.visited_cnt: int = 1
        self.rating: float = 0

    def calc_rating(self):
        if self.last_visited is None:
            raise ValueError("Incorrect date value")
        days = (dt.datetime.today() - self.last_visited).days
        if days == 0:
            self.rating = self.visited_cnt
        elif days < 30:
            self.rating = self.visited_cnt / days
        else:
            self.rating = 0


class FolderHistItem:
    def __init__(self, folder_name: str, last_visited: dt.datetime) -> None:
        self.folder_name = folder_name
        self.last_visited = last_visited
        self.visited_cnt: int = 1
        self.rating: float = 0

    def calc_rating(self):
        if self.last_visited is None:
            raise ValueError("Incorrect date value")
        days = (dt.datetime.today() - self.last_visited).days
        if days == 0:
            self.rating = self.visited_cnt
        else:
            self.rating = self.visited_cnt / days



