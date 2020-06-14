import wx
import browser
import menu
import constants as cn
import config
import pickle
import os
import dir_watcher
from operator import itemgetter
from pathlib import Path
import fnmatch
import wx.aui as aui
import dialogs
import traceback
from threading import Thread
import wx.adv
import sys


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=cn.CN_APP_NAME, size=(600, 500), style=wx.DEFAULT_FRAME_STYLE)
        self.cmd_ids = {}
        self.menu_bar = menu.MainMenu(self)
        self.SetMenuBar(self.menu_bar)
        self.tb = None
        self.app_conf = config.NavigatorConf()
        self.dir_cache = DirCache(self)
        self.SetIcon(wx.Icon(cn.CN_ICON_FILE_NAME))
        self.im_list = wx.ImageList(16, 16)
        # self.img_folder = None
        # self.img_file = None
        # self.img_go_up = None
        # self.img_arrow_up = None
        # self.img_arrow_down = None
        # self.splitter = None
        # self.left_browser = None
        # self.right_browser = None
        self.sizer = None

        self.InitUI()
        self.process_args()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def process_args(self):
        if len(sys.argv) > 1:
            opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
            args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
            if "-w" in opts:
                sys.excepthook = self.except_hook
                self.show_message("Output redirected to UI")
        else:
            pass

    def run_in_thread(self, target, args):
        th = Thread(target=target, args=args)
        th.start()

    def except_hook(self, type, value, tb):
        message = ''.join(traceback.format_exception(type, value, tb))
        wx.LogError(message)

    def get_active_win(self):
        win = self.FindFocus()
        if isinstance(win, browser.Browser):
            return win.page_ctrl
        else:
            raise Exception("Cannot find active page ctrl")

    def get_inactive_win(self):
        win = self.FindFocus()
        if isinstance(win, browser.Browser):
            if win.page_ctrl.is_left:
                return self.right_browser
            else:
                return self.left_browser
        else:
            raise Exception("active " + str(type(win)))

    def return_focus(self):
        self.splitter.SetFocus()

    def change_win_focus(self):
        win = self.FindFocus()
        if isinstance(win, aui.AuiTabCtrl):
            if win.GetParent() == self.left_browser:
                self.right_browser.get_active_browser().SetFocus()
            elif win.GetParent() == self.right_browser:
                self.left_browser.get_active_browser().SetFocus()

    def read_last_conf(self, conf_file, app_conf):
        try:
            with open(conf_file, 'rb') as ac:
                return pickle.load(ac)
        except IOError:
            # self.log_error("Cannot read app configuration '%s'." % conf_file)
            return app_conf

    def write_last_conf(self, conf_file, app_conf):
        try:
            app_conf.size = self.GetSize()
            app_conf.pos = self.GetPosition()
            with open(conf_file, 'wb') as ac:
                pickle.dump(app_conf, ac)
        except IOError:
            self.log_error("Cannot save project file '%s'." % conf_file)

    def InitUI(self):

        self.Freeze()

        self.app_conf = self.read_last_conf(cn.CN_APP_CONFIG, self.app_conf)

        self.img_folder = self.im_list.Add(wx.Bitmap(cn.CN_IM_FOLDER, wx.BITMAP_TYPE_PNG))
        self.img_file = self.im_list.Add(wx.Bitmap(cn.CN_IM_FILE, wx.BITMAP_TYPE_PNG))
        self.img_go_up = self.im_list.Add(wx.Bitmap(cn.CN_IM_GO_UP, wx.BITMAP_TYPE_PNG))
        self.img_arrow_up = self.im_list.Add(wx.Bitmap(cn.CN_IM_ARROW_UP, wx.BITMAP_TYPE_PNG))
        self.img_arrow_down = self.im_list.Add(wx.Bitmap(cn.CN_IM_ARROW_DOWN, wx.BITMAP_TYPE_PNG))
        self.img_hard_disk = self.im_list.Add(wx.Bitmap(cn.CN_IM_HARD_DISK, wx.BITMAP_TYPE_PNG))
        self.img_add = self.im_list.Add(wx.Bitmap(cn.CN_IM_ADD, wx.BITMAP_TYPE_PNG))
        self.img_tools = self.im_list.Add(wx.Bitmap(cn.CN_IM_TOOLS, wx.BITMAP_TYPE_PNG))
        self.img_home = self.im_list.Add(wx.Bitmap(cn.CN_IM_HOME, wx.BITMAP_TYPE_PNG))
        self.img_anchor = self.im_list.Add(wx.Bitmap(cn.CN_IM_ANCHOR, wx.BITMAP_TYPE_PNG))

        self.splitter = wx.SplitterWindow(self, cn.ID_SPLITTER, style=wx.SP_BORDER)
        self.splitter.SetMinimumPaneSize(10)

        self.left_browser = browser.BrowserCtrl(self.splitter, self, self.im_list, self.app_conf.left_browser,
                                                is_left=True)
        self.right_browser = browser.BrowserCtrl(self.splitter, self, self.im_list, self.app_conf.right_browser,
                                                 is_left=False)
        self.splitter.SplitVertically(self.left_browser, self.right_browser)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_SPLITTER_DCLICK, self.on_db_click, id=cn.ID_SPLITTER)

        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        btn_size = (60, 23)
        buttons = [CmdBtn(self, self.cmd_ids[menu.RENAME], "F2 Rename", size=btn_size),
                   CmdBtn(self, self.cmd_ids[menu.VIEW], "F3 View", size=btn_size),
                   CmdBtn(self, self.cmd_ids[menu.EDIT], "F4 Edit", size=btn_size),
                   CmdBtn(self, self.cmd_ids[menu.COPY], "F5 Copy", size=btn_size),
                   CmdBtn(self, self.cmd_ids[menu.MOVE], "F6 Move", size=btn_size),
                   CmdBtn(self, self.cmd_ids[menu.NEW_FOLDER], "F7 Mkdir", size=btn_size),
                   CmdBtn(self, self.cmd_ids[menu.DELETE], "F8 Delete", size=btn_size),
                   CmdBtn(self, self.cmd_ids[menu.NEW_FILE], "F9 Mkfile", size=btn_size)]

        for btn in buttons:
            self.btn_sizer.Add(btn, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
            # btn.Bind(wx.EVT_BUTTON, self.menu_bar.on_click, id=btn.GetId())

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitter, proportion=1, flag=wx.EXPAND)
        self.sizer.Add(self.btn_sizer, proportion=0, flag=wx.EXPAND)

        self.SetSizer(self.sizer)
        # self.SetMinSize(self.GetEffectiveMinSize())

        if self.app_conf.size:
            self.SetSize(self.app_conf.size)
            self.SetPosition(self.app_conf.pos)
        else:
            self.SetSize((600, 500))
            self.Center()

        self.SetDefaultItem(self.left_browser)
        self.left_browser.get_active_browser().SetFocus()
        self.Thaw()

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
        # dlg = wx.MessageBox(text, caption=cn.CN_APP_NAME)
        # dlg = dialogs.messageDialog(parent=self, message=text, title=cn.CN_APP_NAME)
        # dlg = dialogs.findDialog(parent=self, searchText='text to find', wholeWordsOnly=0, caseSensitive=0)
        dlg.ShowModal()

    def get_question_feedback(self, question, caption=cn.CN_APP_NAME):
        dlg = wx.MessageDialog(self, question, style=wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION,
                               caption=caption)
        return dlg.ShowModal()

    def log_error(self, message):
        # wx.LogError(message)
        self.show_message(message)

    def release_resources(self):
        self.dir_cache.release_resources()
        del self.im_list

    # COMMANDS

    def rename(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        selected = b.get_selected()
        if len(selected) != 1:
            self.show_message("Select one item")
        else:
            old_name = selected[0]
            with dialogs.RenameDlg(self, old_name) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    self.run_in_thread(target=b.shell_rename, args=(os.path.join(b.path, old_name),
                                                                    os.path.join(b.path, dlg.get_new_names()[0]),
                                                                    dlg.cb_rename.IsChecked()))

    def view(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        b.shell_viewer(folders, files)

    def copy(self, folders=None, files=None, dst_path=""):
        win = self.get_active_win()
        b = win.get_active_browser()
        if folders is not None or files is not None:
            if folders:
                path = str(Path(folders[0]).parent)
            else:
                path = str(Path(files[0]).parent)
            dst = dst_path
        else:
            path = b.path
            folders, files = b.get_selected_files_folders()
            inactive = self.get_inactive_win()
            if not inactive:
                raise Exception("Cannot determine inactive window")
            else:
                dst = str(inactive.get_active_browser().path)
        if folders or files:
            opr_count = "Copy " + str(len(folders)) + " folder(s) and " + str(len(files)) + " file(s)"
            src = "From: " + str(path) + " to"
            with dialogs.CopyMoveDlg(self, title="Copy", opr_count=opr_count, src=src, dst=dst) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    self.run_in_thread(target=b.shell_copy,
                                       args=(folders + files, dlg.get_dst(), dlg.cb_rename.IsChecked()))
        else:
            self.show_message("No items selected")

    def move(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        if folders or files:
            opr_count = "Move " + str(len(folders)) + " folder(s) and " + str(len(files)) + " file(s)"
            src = "From: " + str(b.path) + " to"
            inactive = self.get_inactive_win()
            if not inactive:
                raise Exception("Cannot determine inactive window")
            else:
                dst = str(inactive.get_active_browser().path)
            with dialogs.CopyMoveDlg(self, title="Move", opr_count=opr_count, src=src, dst=dst) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    self.run_in_thread(target=b.shell_move,
                                       args=(folders + files, dlg.get_dst(), dlg.cb_rename.IsChecked()))
        else:
            self.show_message("No items selected")

    def new_folder(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        def_name = folders[0].name if folders else "new_folder"
        with dialogs.NewFolderDlg(self, b.path, def_name) as dlg:
            if dlg.show_modal() == wx.ID_OK:
                folders = dlg.get_new_names()
                for f in folders:
                    path = b.path
                    for part in Path(f).parts:
                        path = path.joinpath(part.rstrip())
                        if not path.exists():
                            b.shell_new_folder(str(path))

    def delete(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        if folders or files:
            message = "The following items will be deleted. Are you sure?"
            if folders:
                message += "<br/>" + str(len(folders)) + " folder(s): <b>" + \
                           ", ".join([f.name for f in folders]) + "</b>"
            if files:
                message += "<br/>" + str(len(files)) + " file(s): <b>" + \
                           ", ".join([f.name for f in files]) + "</b>"
            with dialogs.DeleteDlg(self, message) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    self.run_in_thread(target=b.shell_delete, args=(folders + files, dlg.cb_perm.IsChecked()))
        else:
            self.show_message("No items selected")

    def new_file(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        def_name = files[0].name if files else "new_file.txt"
        with dialogs.NewFileDlg(self, b.path, def_name) as dlg:
            if dlg.show_modal() == wx.ID_OK:
                file_names = dlg.get_new_names()
                for f in file_names:
                    path = b.path.joinpath(f)
                    b.shell_new_file(path)
                    if dlg.cb_open.IsChecked():
                        b.open_file(path)

    def on_create_shortcut(self, e):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        if folders or files:
            opr_count = "Create shortcut(s) for " + str(len(folders)) + " folder(s) and " + str(len(files)) + " file(s)"
            src = "From: " + str(b.path) + " to"
            inactive = self.get_inactive_win()
            if not inactive:
                raise Exception("Cannot determine inactive window")
            else:
                dst = str(inactive.get_active_browser().path)
            with dialogs.CopyMoveDlg(self, title="Create shortcut(s)", opr_count=opr_count, src=src, dst=dst) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    for f in folders:
                        b.shell_shortcut(path=dlg.get_dst(),
                                         lnk_name=f.name + ".lnk",
                                         target=os.path.join(b.path, f.name))
                    for f in files:
                        b.shell_shortcut(path=dlg.get_dst(),
                                         lnk_name=f.name + ".lnk",
                                         target=os.path.join(b.path, f.name))
        else:
            self.show_message("No items selected")


    def on_copy2same(self, e):
        self.show_message("Copy to the same folder not implemented")

    def select_all(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        b.select_all()

    def invert_selection(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        b.invert_selection()


class CmdBtn(wx.Button):
    def __init__(self, parent, id, label, size):
        super().__init__(parent=parent, id=id, label=label, size=size)
        self.frame = parent
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)

    def AcceptsFocus(self):
        return False

    def AcceptsFocusFromKeyboard(self):
        return False

    def on_focus(self, e):
        self.frame.return_focus()
        self.frame.menu_bar.exec_cmd_id(self.GetId())


class DirCacheItem:
    def __init__(self, frame, dir_name):
        if not dir_name:
            return
        self.dir_name = dir_name
        self.dir_items = []
        self.file_items = []
        self.open_dir(dir_name)
        self.watcher = dir_watcher.DirWatcher(frame=frame, dir_name=dir_name, dir_items=self.dir_items,
                                              file_items=self.file_items)

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
    def __init__(self, frame):
        self.frame = frame
        self._dict = {}

    def get_dir(self, dir_name, conf):
        if isinstance(dir_name, str):
            print("got str", dir_name)
        if dir_name not in self._dict.keys():
            # print("DATA READ", dir_name)
            self._dict[dir_name] = DirCacheItem(frame=self.frame, dir_name=dir_name)
        pattern = conf.pattern if conf.use_pattern else "*"
        return sorted([d for d in self._dict[dir_name].dir_items if fnmatch.fnmatch(d[cn.CN_COL_NAME], pattern)],
                      key=itemgetter(conf.sort_key), reverse=conf.sort_desc) + \
               sorted([f for f in self._dict[dir_name].file_items if fnmatch.fnmatch(f[cn.CN_COL_NAME], pattern)],
                      key=itemgetter(conf.sort_key), reverse=conf.sort_desc)

    def release_resources(self):
        for item in self._dict.keys():
            th = self._dict[item].watcher
            if th.is_alive():
                th.terminate()
                th.join()

    def delete_cache_item(self, dir_name):

        def remove_watcher(dir):
            th = self._dict[dir].watcher
            if th.is_alive():
                th.terminate()
                th.join()

        lst = list(self._dict.keys())
        for item in lst:
            if str(item).startswith(dir_name):
                remove_watcher(item)
                del self._dict[item]






