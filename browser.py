import wx
import os
from pathlib import Path
import util
import constants as cn
from operator import itemgetter
import path_pnl
import win32gui
from win32com.shell import shell, shellcon
import win32api
import win32con
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import filter_pnl
import dir_watcher


CN_MAX_HIST_COUNT = 20


class BrowserPnl(wx.Panel):
    def __init__(self, parent, frame, im_list, conf):
        super().__init__(parent=parent)
        self.frame = frame
        self.path_pnl = path_pnl.PathPanel(self, self.frame)
        self.browser = Browser(self, frame, im_list, conf)
        self.filter_pnl = filter_pnl.FilterPnl(self, self.frame, self.browser)
        self.browser.set_references(self.path_pnl, self.filter_pnl)
        self.path_pnl.hist_menu.set_browser(self.browser)
        self.browser.open_dir(conf.last_path)
        self.top_down_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_down_sizer.Add(self.path_pnl, flag=wx.EXPAND)
        self.top_down_sizer.Add(self.browser, flag=wx.EXPAND, proportion=1)
        self.top_down_sizer.Add(self.filter_pnl, flag=wx.EXPAND)

        self.SetSizerAndFit(self.top_down_sizer)


class Browser(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent, frame, im_list, conf):
        super().__init__(parent=parent, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(0)
        self.parent = parent
        self.frame = frame
        self.path_pnl = None
        self.filter_pnl = None
        self._path = None
        self.watchers = []
        self.conf = conf
        self.conf.pattern = ""
        self.conf.use_pattern = False
        self.history = conf.path_history
        self.extension_images = {}
        self.image_list = im_list
        self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)
        self.columns = ["Name", "Date", "Size"]

        self.init_ui(self.conf)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_db_click)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_col_click)
        self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.on_col_right_click)
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_menu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.on_key_down)

    def init_ui(self, conf):
        for index, name in enumerate(self.columns):
            self.InsertColumn(index, name)
        self.show_hide_cols(self.conf.column_conf)
        self.sort_by_column(conf.sort_key, conf.sort_desc, reread=False)

    def on_key_down(self, e):
        e.Skip()
        if e.GetKeyCode() == wx.WXK_RETURN:
            index = self.GetFocusedItem()
            if index >= 0:
                self.on_item_activated(self.GetItemText(index, 0))
        if e.GetKeyCode() == wx.WXK_ESCAPE:
            self.filter_pnl.enable_filter()

    def show_hide_cols(self, column_conf):
        for col in column_conf.keys():
            if column_conf[col]:
                self.SetColumnWidth(col + 1, 80)
            else:
                self.SetColumnWidth(col + 1, 0)

    def on_col_right_click(self, event):
        menu = ColumnMenu(self, event.GetColumn())
        self.frame.PopupMenu(menu)
        del menu


    def __del__(self):
        self.release_watchers()

    def add_hist_item(self, path):
        if path not in self.history:
            self.history.insert(0, path)
            if len(self.history) > CN_MAX_HIST_COUNT:
                self.history.pop()

    def on_select(self, event):
        index = self.FindItem(-1, cn.CN_GO_BACK)
        if index >= 0:
            self.Select(index, on=0)
        self.update_summary_lbl()

    def clear_selection(self):
        if self.GetSelectedItemCount() > 0:
            for index in range(self.GetItemCount()):
                self.Select(index, 0)

    def select_item(self, index):
        self.clear_selection()
        self.Focus(index)
        self.Select(index)
        self.EnsureVisible(index)

    def select_first_one(self):
        if self.GetItemCount() > 0:
            if self.GetItemText(0) != cn.CN_GO_BACK:
                self.select_item(0)
            else:
                if self.GetItemCount() > 1:
                    self.select_item(1)

    def get_selected(self):
        lst = []
        if self.GetSelectedItemCount() > 0:
            item = self.GetFirstSelected()
            lst.append(self.GetItemText(item))
            while self.GetNextSelected(item) >= 0:
                item = self.GetNextSelected(item)
                lst.append(self.GetItemText(item))
        return lst


    def set_selection(self, selected):
        for item in selected:
            index = self.FindItem(-1, item)
            if index >= 0:
                self.Select(index, on=1)

    def on_menu(self, event):
        if wx.GetKeyState(wx.WXK_CONTROL):
            pass
        else:
            if self.GetFirstSelected() < 0:
                self.get_context_menu(str(self.path), [])
            else:
                items = self.get_selected()
                self.get_context_menu(self.path, items)

    def set_references(self, path_pnl, filter_pnl):
        self.path_pnl = path_pnl
        self.filter_pnl = filter_pnl

    def update_summary_lbl(self):
        files = 0
        folders = 0
        for index in range(self.GetItemCount()):
            img_idx = self.GetItem(index).GetImage()
            if img_idx != self.frame.img_go_up:
                if img_idx:
                    files += 1
                else:
                    folders += 1
        selected = self.GetSelectedItemCount()
        self.parent.filter_pnl.sum_lbl.SetLabel("F " + str(folders) + " f " + str(files) + " S " + str(selected))

    def add_remove(self, added, deleted):
        for item in deleted:
            self.DeleteItem(self.FindItem(-1, item))
        for item in added:
            index = self.Append([item.name,
                                 util.format_date(item.stat().st_mtime),
                                 util.format_size(item.stat().st_size) if item.is_file() else ""])
            if item.is_dir():
                img_id = 0
            else:
                extension = item.suffix if item.suffix else "~$!"
                img_id = self.get_image_id(extension)
            self.SetItemImage(index, img_id)
            self.update_summary_lbl()

    def change_watcher(self, dir):
        if not self.path or (self.path and not self.path.samefile(dir)):
            if self.watchers:
                self.watchers[len(self.watchers) - 1].terminate()
            self.watchers.append(dir_watcher.DirWatcher(dir, self))
            self.watchers[len(self.watchers) - 1].start()

    def release_watchers(self):
        for th in self.watchers:
            if th.is_alive():
                th.terminate()
                th.join()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if self.path_pnl.path_lbl.read_only:
            self.path_pnl.path_lbl.SetValue(self.path_pnl.path_lbl.get_shortcut(str(value)))
        else:
            self.path_pnl.path_lbl.SetValue(str(value))
        self.path_pnl.drive_combo.SetValue(value.anchor)
        os.chdir(str(value))
        self.conf.last_path = str(value)
        self.add_hist_item(str(value))
        self.change_watcher(str(value))
        self.path_pnl.path_lbl.SetInsertionPointEnd()
        self._path = value

    def do_search_folder(self, pattern):
        pattern = "*" if pattern == "" else pattern
        pattern = pattern if pattern.startswith("*") else "*{p}*".format(p=pattern)
        self.conf.pattern = pattern
        self.open_dir(self.path, sel_dir=cn.CN_GO_BACK)

    def sort_by_column(self, sort_key, desc, reread=True):

        def clear_all_others():
            for index, name in enumerate(self.columns):
                if index != sort_key:
                    self.ClearColumnImage(index)

        col = self.GetColumn(sort_key)
        img_idx = self.frame.img_arrow_up if desc else self.frame.img_arrow_down
        clear_all_others()
        self.SetColumnImage(sort_key, img_idx)
        # self.conf.sort_key = sort_key
        # self.conf.sort_desc = col.GetImage() == self.frame.img_arrow_down

        selected = ""
        index = self.GetFirstSelected()
        if index >= 0:
            selected = self.GetItem(self.GetFirstSelected()).GetText()

        if reread:
            self.open_dir(dir_name=self.path, sel_dir=selected)

    def on_col_click(self, event):
        col_index = event.GetColumn()
        col = self.GetColumn(col_index)
        self.conf.sort_key = col_index
        self.conf.sort_desc = col.GetImage() == self.frame.img_arrow_down
        self.sort_by_column(self.conf.sort_key, self.conf.sort_desc)

    def on_item_activated(self, item_name):
        if item_name == cn.CN_GO_BACK:
            if self.path.samefile(self.path.anchor):
                return
            else:
                self.open_dir(dir_name=self.path.parent, sel_dir=self.path.name)
        else:
            new_path = Path(os.path.join(self.path, item_name))
            if util.is_link(new_path):
                raise Exception("Unsupported type")
            elif new_path.is_file():
                self.open_file(new_path)
            elif new_path.is_dir():
                self.open_dir(dir_name=new_path)

    def on_db_click(self, event):
        self.on_item_activated(event.GetText())

    def get_image_id(self, extension):
        """Get the id in the image list for the extension.
        Will add the image if not there already"""
        # Caching
        if extension in self.extension_images:
            return self.extension_images[extension]
        bmp = util.extension_to_bitmap(extension)
        index = self.image_list.Add(bmp)
        self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)
        self.extension_images[extension] = index
        return index

    def open_file(self, file_name):
        win32api.ShellExecute(0, "open", str(file_name), "", '', 1)
        # win32api.ShellExecute(0, "open", "notepad", "", '.', 1)

    def open_dir(self, dir_name, sel_dir=""):
        self.open_directory(dir_name, sel_dir, self.conf)

    def open_directory(self, dir_name, sel_dir, conf):
        if not sel_dir and self.GetFirstSelected() >= 0:
            sel_dir = self.GetItemText(self.GetFirstSelected())
        temp = self.path
        try:
            # self.filter_pnl.disable_filter(clear_search=True)
            p = Path(dir_name)
            pattern = conf.pattern if conf.use_pattern else "*"
            dir_list = [[x.name.lower(), x.stat().st_mtime, "", x.name]
                        for x in p.glob(pattern) if x.is_dir() and not util.is_hidden(x)]
            file_list = [[x.name.lower(), x.stat().st_mtime, x.stat().st_size, x.name]
                         for x in p.glob(pattern) if x.is_file() and not util.is_hidden(x)]
            dir_list = sorted(dir_list, key=itemgetter(conf.sort_key), reverse=conf.sort_desc)
            file_list = sorted(file_list, key=itemgetter(conf.sort_key), reverse=conf.sort_desc)
            self.path = p
            self.DeleteAllItems()
            if not self.path.samefile(self.path.anchor):
                index = self.Append([cn.CN_GO_BACK, "", ""])
                self.SetItemImage(index, self.frame.img_go_up)
            for entry in dir_list:
                index = self.Append([entry[3], util.format_date(entry[1]), entry[2]])
                self.SetItemImage(index, self.frame.img_folder)
            for entry in file_list:
                index = self.Append([entry[3], util.format_date(entry[1]), util.format_size(entry[2])])
                file_name = os.path.join(self.path.parent, entry[0])
                file_name = Path(file_name)
                extension = file_name.suffix
                if not extension:
                    extension = "~$!"
                img_id = self.get_image_id(extension)
                self.SetItemImage(index, img_id)
            self.update_summary_lbl()
            self.set_selection([sel_dir])
        except OSError as err:
            self.frame.log_error(str(err))
            self.open_dir(temp)

    def get_context_menu(self, path, file_names=[]):
        file_names = [str(item) for item in file_names]
        path = str(path)
        hwnd = win32gui.GetForegroundWindow()
        # Get an IShellFolder for the desktop.
        desktopFolder = shell.SHGetDesktopFolder()
        if not desktopFolder:
            raise Exception("Failed to get Desktop folder.")
        # Get a pidl for the folder the file is located in.
        eaten, parentPidl, attr = desktopFolder.ParseDisplayName(hwnd, None, path)
        # Get an IShellFolder for the folder the file is located in.
        parentFolder = desktopFolder.BindToObject(parentPidl, None, shell.IID_IShellFolder)
        if file_names:
            # Get a pidl for the file itself.
            pidls = []
            for item in file_names:
                eaten, pidl, attr = parentFolder.ParseDisplayName(hwnd, None, item)
                pidls.append(pidl)
            # Get the IContextMenu for the file.
            i, contextMenu = parentFolder.GetUIObjectOf(hwnd, pidls, shell.IID_IContextMenu, 0)
        else:
            i, contextMenu = desktopFolder.GetUIObjectOf(hwnd, [parentPidl], shell.IID_IContextMenu,
                                                         1)  # <----- where i attempt to get menu for a drive.
        contextMenu_plus = None
        if contextMenu:
            # try to obtain a higher level pointer, first 3 then 2
            try:
                contextMenu_plus = contextMenu.QueryInterface(shell.IID_IContextMenu3, None)
            except Exception:
                try:
                    contextMenu_plus = contextMenu.QueryInterface(shell.IID_IContextMenu2, None)
                except Exception:
                    pass
        else:
            raise Exception("Unable to get context menu interface.")

        if contextMenu_plus:
            contextMenu.Release()  # free initial "v1.0" interface
            contextMenu = contextMenu_plus
        else:  # no higher version supported
            pcmType = 1

        hMenu = win32gui.CreatePopupMenu()
        MIN_SHELL_ID = 1
        MAX_SHELL_ID = -1# 30000

        contextMenu.QueryContextMenu(hMenu, 0, MIN_SHELL_ID, MAX_SHELL_ID, shellcon.CMF_EXPLORE |
                                     shellcon.CMF_CANRENAME)
        x, y = win32gui.GetCursorPos()
        flags = win32gui.TPM_LEFTALIGN | win32gui.TPM_RETURNCMD #| win32gui.TPM_LEFTBUTTON | win32gui.TPM_RIGHTBUTTON
        cmd = win32gui.TrackPopupMenu(hMenu, flags, x, y, 0, hwnd, None)
        if not cmd:
            e = win32api.GetLastError()
            if e:
                s = win32api.FormatMessage(e)
                raise Exception(s)
        CI = (0,  # Mask
              hwnd,  # hwnd
              cmd - MIN_SHELL_ID,  # Verb
              '',  # Parameters
              '',  # Directory
              win32con.SW_SHOWNORMAL,  # Show
              0,  # HotKey
              None  # Icon
              )
        if cmd - MIN_SHELL_ID >= 0:
            contextMenu.InvokeCommand(CI)


class ColumnMenu(wx.Menu):
    def __init__(self, browser, column):
        super().__init__()
        self.column = column
        self.browser = browser
        self.sub_menu = wx.Menu()
        self.header_id = wx.NewId()
        self.header = self.sub_menu.Append(id=self.header_id, item="Header")
        self.content_id = wx.NewId()
        self.content = self.sub_menu.Append(id=self.content_id, item="Content")
        self.column_conf_id = wx.NewId()
        self.column_conf = self.Append(id=self.column_conf_id, item="Select columns...")
        self.column_width = self.Append(id=wx.NewId(), item="Fit column", subMenu=self.sub_menu)

        self.Bind(wx.EVT_MENU, self.on_column_conf, id=self.column_conf_id)
        self.Bind(wx.EVT_MENU, self.on_header, id=self.header_id)
        self.Bind(wx.EVT_MENU, self.on_content, id=self.content_id)

    def on_header(self, e):
        self.browser.SetColumnWidth(self.column, wx.LIST_AUTOSIZE_USEHEADER)

    def on_content(self, e):
        self.browser.SetColumnWidth(self.column, wx.LIST_AUTOSIZE)

    def on_column_conf(self, e):
        lst = self.browser.columns[1:]
        dlg = wx.MultiChoiceDialog(parent=self.browser, message="Select columns to show",
                                   caption=cn.CN_APP_NAME, choices=lst)
        dlg.SetSelections([col for col in self.browser.conf.column_conf.keys() if self.browser.conf.column_conf[col]])
        if dlg.ShowModal() == wx.ID_OK:
            selections = dlg.GetSelections()
            for col in self.browser.conf.column_conf.keys():
                self.browser.conf.column_conf[col] = col in selections
            self.browser.show_hide_cols(self.browser.conf.column_conf)
            if self.browser.conf.sort_key - 1 not in selections:
                self.browser.sort_by_column(0, False, reread=True)
            self.browser.resizeLastColumn(40)
        del dlg
