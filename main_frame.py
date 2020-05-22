import wx
import browser
import menu
import constants as cn
import config
import pickle
import os
import dir_watcher
from operator import itemgetter
import util
from pathlib import Path

ID_SPLITTER = wx.NewId()


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=cn.CN_APP_NAME, size=(600, 500), style=wx.DEFAULT_FRAME_STYLE)
        self.menu_bar = menu.MainMenu(self)
        self.SetMenuBar(self.menu_bar)
        self.app_conf = config.NavigatorConf()
        self.dir_cache = DirCache()
        self.SetIcon(wx.Icon(cn.CN_ICON_FILE_NAME))
        self.im_list = wx.ImageList(16, 16)
        self.img_folder = None
        self.img_file = None
        self.img_go_up = None
        self.img_arrow_up = None
        self.img_arrow_down = None
        self.splitter = None
        self.left_browser = None
        self.right_browser = None
        self.sizer = None

        self.InitUI()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def read_last_conf(self, conf_file, app_conf):
        try:
            with open(conf_file, 'rb') as ac:
                return pickle.load(ac)
        except IOError:
            # self.log_error("Cannot read app configuration '%s'." % conf_file)
            return app_conf

    def write_last_conf(self, conf_file, app_conf):
        try:
            with open(conf_file, 'wb') as ac:
                pickle.dump(app_conf, ac)
        except IOError:
            self.log_error("Cannot save project file '%s'." % file_name)

    def InitUI(self):

        self.app_conf = self.read_last_conf(cn.CN_APP_CONFIG, self.app_conf)

        self.img_folder = self.im_list.Add(wx.Bitmap(cn.CN_IM_FOLDER, wx.BITMAP_TYPE_PNG))
        self.img_file = self.im_list.Add(wx.Bitmap(cn.CN_IM_FILE, wx.BITMAP_TYPE_PNG))
        self.img_go_up = self.im_list.Add(wx.Bitmap(cn.CN_IM_GO_UP, wx.BITMAP_TYPE_PNG))
        self.img_arrow_up = self.im_list.Add(wx.Bitmap(cn.CN_IM_ARROW_UP, wx.BITMAP_TYPE_PNG))
        self.img_arrow_down = self.im_list.Add(wx.Bitmap(cn.CN_IM_ARROW_DOWN, wx.BITMAP_TYPE_PNG))

        self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
        self.splitter.SetMinimumPaneSize(10)

        self.left_browser = browser.BrowserCtrl(self.splitter, self, self.im_list, self.app_conf.left_browser)
        self.right_browser = browser.BrowserCtrl(self.splitter, self, self.im_list, self.app_conf.right_browser)
        self.splitter.SplitVertically(self.left_browser, self.right_browser)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_SPLITTER_DCLICK, self.on_db_click, id=ID_SPLITTER)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitter, 1, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.SetMinSize(self.GetEffectiveMinSize())

        self.Center()

    def on_size(self, e):
        size = self.GetSize()
        self.splitter.SetSashPosition(size.x / 2)

        e.Skip()

    def on_db_click(self, e):
        size = self.GetSize()
        self.splitter.SetSashPosition(size.x / 2)

    def on_close(self, event):
        self.Hide()
        self.release_resources()
        self.write_last_conf(cn.CN_APP_CONFIG, self.app_conf)
        event.Skip()

    def show_message(self, text):
        dlg = wx.MessageDialog(self, text, caption=cn.CN_APP_NAME)
        dlg.ShowModal()

    def log_error(self, message):
        # wx.LogError(message)
        self.show_message(message)

    def release_resources(self):
        # self.left_browser.browser.release_watchers()
        # self.right_browser.browser.release_watchers()
        del self.im_list


class DirCacheItem:
    def __init__(self, dir_name):
        if not dir_name:
            return
        self.dir_name = dir_name
        self.dir_items = []
        self.file_items = []
        self.open_dir(dir_name)
        self.watcher = dir_watcher.DirWatcher(dir_name=dir_name, dir_items=self.dir_items, file_items=self.file_items)

    def open_dir(self, dir_name):
        self.dir_items = []
        self.file_items = []
        with os.scandir(dir_name) as sd:
            for i in sd:
                if i.is_dir():
                    self.dir_items.append([i.name.lower(), i.stat().st_mtime, "", i.name, i.is_dir(), ""])
                else:
                    self.file_items.append([i.name.lower(), i.stat().st_mtime, i.stat().st_size, i.name, i.is_dir(),
                                            Path(i.name).suffix])


class DirCache:
    def __init__(self):
        self._dict = {}

    def get_dir(self, dir_name, conf):
        if dir_name not in self._dict.keys():
            # read the data
            self._dict[dir_name] = DirCacheItem(dir_name=dir_name)
        return sorted(self._dict[dir_name].dir_items, key=itemgetter(conf.sort_key), reverse=conf.sort_desc) + \
               sorted(self._dict[dir_name].file_items, key=itemgetter(conf.sort_key), reverse=conf.sort_desc)







