import wx
from pathlib import Path
import util
import constants as cn
import path_pnl
import win32gui
from win32com.shell import shell, shellcon
import win32api
import win32con
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import filter_pnl
import time
import wx.aui as aui
import win32file
import config
from pubsub import pub
import subprocess
import pythoncom
import os
import winshell
import dialogs

CN_MAX_HIST_COUNT = 20


class Tit:
    def __init__(self, text):
        print(text)
        self.start = time.time()

    def __del__(self):
        print("Elapsed: ", time.time() - self.start)


class BrowserCtrl(aui.AuiNotebook):
    def __init__(self, parent, frame, im_list, conf, is_left):
        super().__init__(parent=parent, style=aui.AUI_NB_TAB_MOVE | aui.AUI_NB_TAB_SPLIT |
                                              aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_TOP)
        self.SetArtProvider(aui.AuiDefaultTabArt())
        self.parent = parent
        self.frame = frame
        self.is_left = is_left
        self.im_list = im_list
        self.conf = conf
        if not conf:
            self.add_new_tab(dir_name="")
        else:
            for tab in conf:
                self.add_tab(tab)

        if self.is_left:
            if self.frame.app_conf.left_active_tab:
                self.SetSelection(self.frame.app_conf.left_active_tab)
        else:
            if self.frame.app_conf.right_active_tab:
                self.SetSelection(self.frame.app_conf.right_active_tab)

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        self.Bind(wx.EVT_CHILD_FOCUS, self.on_child_focus)
        self.Bind(aui.EVT_AUINOTEBOOK_BG_DCLICK, self.on_ctrl_db_click)
        self.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_DOWN, self.on_tab_right_click)

    def on_tab_right_click(self, e):
        screen_pt = wx.GetMousePosition()
        client_pt = self.ScreenToClient(screen_pt)
        tab_index, _ = self.HitTest(client_pt)
        menu = TabMenu(self.frame, self, tab_index)
        self.frame.PopupMenu(menu)
        del menu

    def on_ctrl_db_click(self, e):
        self.add_new_tab(self.get_active_browser().path)

    def add_tab(self, tab_conf, select=False):
        self.Freeze()
        tab = BrowserPnl(self, self.frame, self.im_list, tab_conf)
        self.AddPage(page=tab, caption="tab", select=select)
        self.Thaw()

    def add_new_tab(self, dir_name):
        tab_conf = config.BrowserConf()
        tab_conf.last_path = dir_name if dir_name else Path.home()
        self.conf.append(tab_conf)
        self.add_tab(tab_conf=tab_conf, select=True)

    def close_tab(self, tab_index):
        self.DeletePage(tab_index)
        del self.conf[tab_index]

    def duplicate_tab(self, tab_index):
        self.add_new_tab(self.conf[tab_index].last_path)

    def on_child_focus(self, e):
        if isinstance(wx.Window.FindFocus(), aui.AuiTabCtrl):
            self.frame.change_win_focus()
        e.Skip()

    def lock_tab(self, tab_index, tab_name=None):
        self.conf[tab_index].lock_tab(user_tab_name=tab_name)
        self.SetPageText(tab_index, self.conf[tab_index].tab_name)

    def unlock_tab(self, tab_index):
        self.conf[tab_index].unlock_tab()
        self.SetPageText(tab_index, self.conf[tab_index].tab_name)

    def on_page_changed(self, e):
        b = self.get_active_browser()
        b.open_dir(dir_name=self.conf[self.GetSelection()].last_path)
        b.SetFocus()
        if self.is_left:
            self.frame.app_conf.left_active_tab = self.GetSelection()
        else:
            self.frame.app_conf.right_active_tab = self.GetSelection()
        e.Skip()

    def get_active_browser(self):
        return self.GetCurrentPage().browser


class BrowserPnl(wx.Panel):
    def __init__(self, parent, frame, im_list, conf):
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame
        self.path_pnl = path_pnl.PathPanel(self, self.frame)
        # self.path_pnl = dir_label.DirLabel(self, self.frame)
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


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, object, target_processor):
        super().__init__()
        self.object = object
        self.target_processor = target_processor

    def OnDropFiles(self, x, y, filenames):
        return self.target_processor(x, y, filenames)

    def OnDragOver(self, x, y, defResult):
        src_id = self.object.drag_src.win_id if self.object.drag_src else -1
        tgt_id = self.object.drag_tgt.object.win_id
        item, flags = self.object.HitTest((x, y))
        if src_id == tgt_id:
            if item < 0:
                return wx.DragNone
            else:
                path = self.object.path.joinpath(self.object.GetItemText(item))
                print(path)
                return wx.DragCopy if path.is_dir() else wx.DragNone
        else:
            return wx.DragCopy


class MyDropSource(wx.DropSource):
    def __init__(self, win_id, data):
        super().__init__(data=data)
        self.win_id = win_id


class Browser(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent, frame, im_list, conf):
        self.win_id = wx.NewId()
        super().__init__(parent=parent, style=wx.LC_REPORT | wx.LC_VIRTUAL, id=self.win_id)
        ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(0)
        self.parent = parent
        self.page_ctrl = self.parent.parent
        self.frame = frame
        self.path_pnl = None
        self.filter_pnl = None
        self._path = None
        self.root = None
        self.dir_cache = []
        self.conf = conf
        self.conf.pattern = ""
        self.conf.use_pattern = False
        self.history = conf.path_history
        self.extension_images = {}
        self.image_list = im_list
        self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)
        self.columns = ["Name", "Date", "Size"]
        self.drag_src = None
        self.drag_tgt = MyFileDropTarget(self, self.on_process_dropped_files)
        self.SetDropTarget(self.drag_tgt)

        self.init_ui(self.conf)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_db_click)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_col_click)
        self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.on_col_right_click)
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_menu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_SET_FOCUS, self.on_browser_focus)
        # self.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.on_start_drag, id=self.win_id)
        self.register_listener(topic=cn.CN_TOPIC_DIR_CHG)

    def on_process_dropped_files(self, x, y, file_names):
        src_id = self.drag_src.win_id if self.drag_src else -1
        tgt_id = self.drag_tgt.object.win_id
        same_win = src_id == tgt_id
        if same_win:
            return True
        else:
            if src_id < 0:
                self.SetFocus()
            folders = [f for f in file_names if Path(f).exists() and Path(f).is_dir()]
            files = [f for f in file_names if Path(f).exists() and Path(f).is_file()]
            self.frame.copy(folders, files, str(self.path))
            return True

    def on_start_drag(self, e):
        selected = self.get_selected()
        if not selected:
            return
        files = wx.FileDataObject()
        for item in selected:
            files.AddFile(str(self.path.joinpath(item)))
        self.drag_src = MyDropSource(self.win_id, files)
        result = self.drag_src.DoDragDrop()
        self.drag_src = None

    def on_browser_focus(self, e):
        os.chdir(str(self.path))
        self.path_pnl.path_lbl.Refresh()
        self.frame.get_inactive_win().get_active_browser().path_pnl.path_lbl.Refresh()
        e.Skip()

    def on_kill_focus(self, e):
        self.path_pnl.path_lbl.Refresh()
        e.Skip()

    def __repr__(self):
        return str(self.path)

    def register_listener(self, topic):
        pub.subscribe(self.listen_dir_changes, topic)

    def listen_dir_changes(self, dir_name, added, deleted):
        if self.path.samefile(dir_name):
            for item_name in deleted:
                self.remove_item(item_name=item_name)
            self.refresh_list(dir_name=dir_name, conf=self.conf, to_select=[])

    def get_source_id_in_list(self, item_name):
        print("cache before delete", [item[cn.CN_COL_NAME] for item in self.dir_cache])
        index = [item[cn.CN_COL_NAME] for item in self.dir_cache].index(item_name)
        # index = self.dir_cache.index(item_name)
        return index if self.root else index + 1

    def remove_item(self, item_name):
        index = self.FindItem(-1, item_name)
        if index >= 0:
            self.DeleteItem(index)

    def get_tab_index(self):
        return self.page_ctrl.GetPageIndex(self.parent)

    def set_tab_name(self, name):
        index = self.get_tab_index()
        self.page_ctrl.SetPageText(index, name)

    def OnGetItemText(self, item, col):

        def gci(item, col):
            # print(item, col)
            if col == cn.CN_COL_DATE:
                return util.format_date(self.dir_cache[item][col])
            elif col == cn.CN_COL_SIZE:
                return util.format_size(self.dir_cache[item][col])
            else:
                return self.dir_cache[item][col]

        if item == 0:
            if not self.root:
                return cn.CN_GO_BACK if col == 0 else ""
            else:
                return gci(0, cn.CN_COL_NAME if col == 0 else col)
        else:
            return gci(item - 1 if not self.root else item, cn.CN_COL_NAME if col == 0 else col)

    def OnGetItemImage(self, item):
        if item == 0 and not self.root:
            return self.frame.img_go_up
        if self.dir_cache[item - 1 if not self.root else item][cn.CN_COL_ISDIR]:
            return self.frame.img_folder
        else:
            extension = self.dir_cache[item - 1 if not self.root else item][cn.CN_COL_EXT]
            if not extension:
                extension = "~$!"
            return self.get_image_id(extension)

    def OnGetItemAttr(self, item):
        # if item % 3 == 1:
        #     return self.attr1
        # elif item % 3 == 2:
        #     return self.attr2
        # else:
        return None

    def init_ui(self, conf):
        for index, name in enumerate(self.columns):
            self.InsertColumn(index, name)
        self.show_hide_cols(self.conf.column_conf)
        self.sort_by_column(conf.sort_key, conf.sort_desc, reread=False)


    def on_key_down(self, e):
        # e.Skip()
        # if e.GetKeyCode() == wx.WXK_RETURN:
        #     index = self.GetFocusedItem()
        #     if index >= 0:
        #         self.on_item_activated(self.GetItemText(index, 0))
        if e.GetKeyCode() == wx.WXK_ESCAPE:
            print("escape")
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
        # self.release_watchers()
        pass

    def add_hist_item(self, path):
        if path not in self.history:
            self.history.insert(0, path)
            if len(self.history) > CN_MAX_HIST_COUNT:
                self.history.pop()

    def on_select(self, event):
        # index = self.FindItem(-1, cn.CN_GO_BACK)
        # if index >= 0:
        #     self.Select(index, on=0)
        # print("selected")
        wx.CallAfter(self.update_summary_lbl)
        event.Skip()

    def on_deselect(self, e):
        # print("deselected")
        pass

    def select_all(self):
        for i in range(self.GetItemCount()):
            self.Select(i)
        if not self.root and self.GetItemCount() > 0:
            self.Select(0, 0)

    def invert_selection(self):
        for i in range(self.GetItemCount()):
            self.Select(i, 0 if self.IsSelected(i) else 1)
        if not self.root and self.GetItemCount() > 0:
            self.Select(0, 0)

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

        def append(_lst, _item):
            if _item != cn.CN_GO_BACK:
                _lst.append(_item)

        lst = []
        if self.GetSelectedItemCount() > 0:
            item = self.GetFirstSelected()
            append(lst, self.GetItemText(item))
            while self.GetNextSelected(item) >= 0:
                item = self.GetNextSelected(item)
                append(lst, self.GetItemText(item))
        return lst

    def get_selected_files_folders(self):
        lst = self.get_selected()
        files = []
        folders = []
        for item in lst:
            path = self.path.joinpath(item)
            if path.is_dir():
                folders.append(path)
            elif path.is_file():
                files.append(path)
            else:
                raise Exception("Unknown object type:" + path)
        return folders, files

    def set_selection(self, selected):
        if not selected:
            return
        self.clear_selection()
        for item in selected:
            index = self.FindItem(-1, item)
            if index >= 0:
                self.Select(index, on=1)
                if len(selected) == 1:
                    self.Focus(index)

    def on_menu(self, event):
        if wx.GetKeyState(wx.WXK_CONTROL):
            pass
        else:
            if self.GetFirstSelected() < 0:
                self.get_context_menu2(str(self.path), [])
            else:
                items = self.get_selected()
                # items = [str(self.path.joinpath(item)) for item in self.get_selected()]
                self.get_context_menu2(self.path, items)

    def set_references(self, path_pnl, filter_pnl):
        self.path_pnl = path_pnl
        self.filter_pnl = filter_pnl

    def update_summary_lbl(self):
        files = 0
        folders = 0
        for item in self.dir_cache:
            if item[4]:
                folders += 1
            else:
                files += 1
        selected = self.GetSelectedItemCount()
        self.parent.filter_pnl.sum_lbl.SetLabel("F " + str(folders) + " f " + str(files) + " S " + str(selected))

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self.path_pnl.drive_combo.SetValue(value.anchor)
        os.chdir(str(value))
        self.conf.last_path = value
        wx.CallAfter(self.set_tab_name, self.conf.tab_name)
        wx.CallAfter(self.path_pnl.set_value, str(value))
        self.add_hist_item(str(value))
        self.root = value.samefile(value.anchor)
        self._path = value

    def do_search_folder(self, pattern):
        pattern = "*" if pattern == "" else pattern
        pattern = pattern if pattern.startswith("*") else "*{p}*".format(p=pattern)
        self.conf.pattern = pattern
        self.open_dir(self.path, sel_dir=cn.CN_GO_BACK)
        self.select_first_one()

    def sort_by_column(self, sort_key, desc, reread=True):

        def clear_all_others():
            for index, name in enumerate(self.columns):
                if index != sort_key:
                    self.ClearColumnImage(index)

        img_idx = self.frame.img_arrow_up if desc else self.frame.img_arrow_down
        clear_all_others()
        self.SetColumnImage(sort_key, img_idx)

        if reread:
            self.open_dir(dir_name=self.path)

    def on_col_click(self, event):
        col_index = event.GetColumn()
        col = self.GetColumn(col_index)
        self.conf.sort_key = col_index
        self.conf.sort_desc = col.GetImage() == self.frame.img_arrow_down
        self.sort_by_column(self.conf.sort_key, self.conf.sort_desc)

    def on_item_activated(self, item_name):
        t = Tit("on_item_activated")
        if item_name == cn.CN_GO_BACK:
            if self.path.samefile(self.path.anchor):
                return
            else:
                self.open_dir(dir_name=self.path.parent, sel_dir=self.path.name)
        else:
            new_path = Path(os.path.join(self.path, item_name))
            if new_path.suffix.lower() == ".lnk":
                lnk = ShellShortcut()
                res = lnk.load(str(new_path))
                new_path = Path(res)
                del lnk
            if new_path.is_file():
                self.open_file(new_path)
            elif new_path.is_dir():
                self.open_dir(dir_name=new_path)
        del t

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
        # hwnd = win32gui.GetForegroundWindow()
        # desktopFolder = shell.SHGetDesktopFolder()
        # eaten, parentPidl, attr = desktopFolder.ParseDisplayName(hwnd, None, str(self.path))
        # parentFolder = desktopFolder.BindToObject(parentPidl, None, shell.IID_IShellFolder)
        # eaten, pidl, attr = parentFolder.ParseDisplayName(hwnd, None, file_name.name)
        dict = shell.ShellExecuteEx(fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                                    nShow=win32con.SW_NORMAL,
                                    lpVerb="Open",
                                    lpFile=str(file_name))
        # print(dict)
        # hh = dict['hInstApp']
        # ret = win32event.WaitForSingleObject(hh, -1)
        # print(ret)
        # pidl = shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_DESKTOP)
        # print("The desktop is at", shell.SHGetPathFromIDList(pidl))
        # shell.ShellExecuteEx(fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
        #                      nShow=win32con.SW_NORMAL,
        #                      lpClass="folder",
        #                      lpVerb="explore",
        #                      lpIDList=pidl)
        # win32api.ShellExecute(0, "open", str(file_name), "", '', 1)
        # win32api.ShellExecute(0, "open", "notepad", "", '.', 1)

    def get_next_dir(self, path):
        if path.exists():
            return path
        for parent in path.parents:
            if parent.exists():
                return parent
        return path.home

    def open_dir(self, dir_name, sel_dir=""):
        path = Path(dir_name)
        if path.exists():
            self.open_directory(dir_name, sel_dir, self.conf)
        else:
            self.open_directory(str(self.get_next_dir(path)), cn.CN_GO_BACK, self.conf)


    def open_directory(self, dir_name, sel_dir, conf):
        if self.path is not None:
            if self.path.samefile(dir_name):
                to_select = self.get_selected()
            else:
                self.filter_pnl.disable_filter(clear_search=False)
                if sel_dir:
                    to_select = [sel_dir]
                else:
                    to_select = [cn.CN_GO_BACK]
        else:
            if sel_dir:
                to_select = [sel_dir]
            else:
                to_select = [cn.CN_GO_BACK]
        temp = self.path
        try:
            self.refresh_list(dir_name=self.get_next_dir(Path(dir_name)), conf=conf, to_select=to_select)
        except OSError as err:
            self.frame.log_error(str(err))
            print(temp)
            self.open_dir(temp)

    def refresh_list(self, dir_name, conf, to_select):
        self.dir_cache = self.frame.dir_cache.get_dir(dir_name=Path(dir_name), conf=conf)
        self.path = Path(dir_name)
        count = len(self.dir_cache)
        if not self.root:
            count += 1
        self.SetItemCount(count)
        if count:
            wx.CallAfter(self.Refresh)
            wx.CallAfter(self.set_selection, to_select)
        else:
            self.DeleteAllItems()
        wx.CallAfter(self.update_summary_lbl)

    def shell_copy(self, src, dst, auto_rename=False):
        """
        Copy files and directories using Windows shell.

        :param src: Path or a list of paths to copy. Filename portion of a path
                    (but not directory portion) can contain wildcards ``*`` and
                    ``?``.
        :param dst: destination directory.
        :param auto_rename: if ''False'' then overwrite else auto rename
        :returns: ``True`` if the operation completed successfully,
                  ``False`` if it was aborted by user (completed partially).
        :raises: ``WindowsError`` if anything went wrong. Typically, when source
                 file was not found.

        .. seealso:
            `SHFileperation on MSDN <http://msdn.microsoft.com/en-us/library/windows/desktop/bb762164(v=vs.85).aspx>`
        """
        if isinstance(src, str):  # in Py3 replace basestring with str
            src = os.path.abspath(src)
        else:  # iterable
            src = '\0'.join(os.path.abspath(path) for path in src)

        flags = shellcon.FOF_NOCONFIRMMKDIR
        if auto_rename:
            flags = flags | shellcon.FOF_RENAMEONCOLLISION

        result, aborted = shell.SHFileOperation((
            0,
            shellcon.FO_COPY,
            src,
            os.path.abspath(dst),
            flags,
            None,
            None))

        if not aborted and result != 0:
            # Note: raising a WindowsError with correct error code is quite
            # difficult due to SHFileOperation historical idiosyncrasies.
            # Therefore we simply pass a message.
            wx.CallAfter(wx.LogError, "Cannot copy. Windows error - SHFileOperation failed: 0x%08x" % result)

        return not aborted

    def shell_move(self, src, dst, auto_rename=False):
        """
        Move files and directories using Windows shell.

        :param src: Path or a list of paths to copy. Filename portion of a path
                    (but not directory portion) can contain wildcards ``*`` and
                    ``?``.
        :param dst: destination directory.
        :param auto_rename: if ''False'' then overwrite else auto rename
        :returns: ``True`` if the operation completed successfully,
                  ``False`` if it was aborted by user (completed partially).
        :raises: ``WindowsError`` if anything went wrong. Typically, when source
                 file was not found.

        .. seealso:
            `SHFileperation on MSDN <http://msdn.microsoft.com/en-us/library/windows/desktop/bb762164(v=vs.85).aspx>`
        """
        if isinstance(src, str):  # in Py3 replace basestring with str
            src = os.path.abspath(src)
        else:  # iterable
            src = '\0'.join(os.path.abspath(path) for path in src)

        flags = shellcon.FOF_NOCONFIRMMKDIR
        if auto_rename:
            flags = flags | shellcon.FOF_RENAMEONCOLLISION

        result, aborted = shell.SHFileOperation((
            0,
            shellcon.FO_MOVE,
            src,
            os.path.abspath(dst),
            flags,
            None,
            None))

        if not aborted and result != 0:
            # Note: raising a WindowsError with correct error code is quite
            # difficult due to SHFileOperation historical idiosyncrasies.
            # Therefore we simply pass a message.
            wx.CallAfter(wx.LogError, "Cannot copy. Windows error - SHFileOperation failed: 0x%08x" % result)

        return not aborted

    def shell_rename(self, src, dst, auto_rename=False):
        """
        Rename files and directories using Windows shell.

        :param src: Path or a list of paths to copy. Filename portion of a path
                    (but not directory portion) can contain wildcards ``*`` and
                    ``?``.
        :param dst: destination directory.
        :param auto_rename: if ''False'' then overwrite else auto rename
        :returns: ``True`` if the operation completed successfully,
                  ``False`` if it was aborted by user (completed partially).
        :raises: ``WindowsError`` if anything went wrong. Typically, when source
                 file was not found.

        .. seealso:
            `SHFileperation on MSDN <http://msdn.microsoft.com/en-us/library/windows/desktop/bb762164(v=vs.85).aspx>`
        """
        if isinstance(src, str):  # in Py3 replace basestring with str
            src = os.path.abspath(src)
        else:  # iterable
            src = '\0'.join(os.path.abspath(path) for path in src)

        flags = shellcon.FOF_NOCONFIRMMKDIR | shellcon.FOF_SILENT
        if auto_rename:
            print("will replace")
            flags = flags | shellcon.FOF_RENAMEONCOLLISION

        result, aborted = shell.SHFileOperation((
            0,
            shellcon.FO_RENAME,
            src,
            os.path.abspath(dst),
            flags,
            None,
            None))

        if not aborted and result != 0:
            # Note: raising a WindowsError with correct error code is quite
            # difficult due to SHFileOperation historical idiosyncrasies.
            # Therefore we simply pass a message.
            wx.CallAfter(wx.LogError, "Cannot rename. Windows error - SHFileOperation failed: 0x%08x" % result)

        return not aborted

    def shell_delete(self, src, hard_delete):
        """
        Move files and directories using Windows shell.

        :param src: Path or a list of paths to copy. Filename portion of a path
                    (but not directory portion) can contain wildcards ``*`` and
                    ``?``.
        :returns: ``True`` if the operation completed successfully,
                  ``False`` if it was aborted by user (completed partially).
        :raises: ``WindowsError`` if anything went wrong. Typically, when source
                 file was not found.

        .. seealso:
            `SHFileperation on MSDN <http://msdn.microsoft.com/en-us/library/windows/desktop/bb762164(v=vs.85).aspx>`
        """
        for f in src:
            if f.is_dir():
                self.frame.dir_cache.delete_cache_item(dir_name=str(f))

        if isinstance(src, str):  # in Py3 replace basestring with str
            src = os.path.abspath(src)
        else:  # iterable
            src = '\0'.join(os.path.abspath(path) for path in src)

        flags = 0  # shellcon.FOF_SILENT

        if not hard_delete:
            flags |= shellcon.FOF_ALLOWUNDO

        result, aborted = shell.SHFileOperation((
            0,
            shellcon.FO_DELETE,
            src,
            None,
            flags,  # Flags
            None,
            None))

        if not aborted and result != 0:
            # Note: raising a WindowsError with correct error code is quite
            # difficult due to SHFileOperation historical idiosyncrasies.
            # Therefore we simply pass a message.
            wx.CallAfter(wx.LogError, "Cannot delete. Windows error - SHFileOperation failed: 0x%08x" % result)
            # raise WindowsError('SHFileOperation failed: 0x%08x' % result)

        return not aborted

    def shell_new_folder(self, folder_name):
        try:
            win32file.CreateDirectory(folder_name, None)
            return True
        except Exception as e:
            self.frame.log_error(folder_name + " can't be created. " + str(e))
            return False

    def shell_viewer(self, folders, files):
        args = ["pythonw", str(cn.CN_VIEWER_APP), "-r"]
        if files:
            args.extend([str(f) for f in files])
            subprocess.Popen(args, shell=False, cwd=cn.CN_VIEWER_APP.parent)
        elif folders:
            if len(folders) == 1:
                self.frame.show_message("Show folder properties")
            else:
                self.frame.show_message("Selected one folder")
        else:
            self.frame.show_message("No items selected")

    def shell_new_file(self, file_name):
        try:
            handle = win32file.CreateFile(str(file_name),
                                          win32file.GENERIC_WRITE,
                                          win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE |
                                          win32file.FILE_SHARE_DELETE,
                                          None,
                                          win32con.CREATE_NEW,
                                          win32con.FILE_ATTRIBUTE_NORMAL,
                                          None)
            handle.Close()
            return True
        except Exception as e:
            self.frame.log_error(str(file_name) + " can't be created. " + str(e))
            return False

    def shell_shortcut(self, path, lnk_name, target, args=None, desc=None, start_in=None):
        winshell.CreateShortcut(Path=str(os.path.join(path, lnk_name)),
                                Target=str(target),
                                Arguments=str(args),
                                Description=str(desc),
                                StartIn=str(start_in))

    def get_context_menu(self, path, file_names=[]):
        # pythoncom.OleInitialize()
        # file_names = [str(item) for item in file_names]
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
            print(path, file_names)
            for item in file_names:
                eaten, pidl, attr = parentFolder.ParseDisplayName(hwnd, None, item)
                pidls.append(pidl)
            # Get the IContextMenu for the file.
            i, contextMenu = parentFolder.GetUIObjectOf(hwnd, pidls, shell.IID_IContextMenu, 0)
        else:
            i, contextMenu = desktopFolder.GetUIObjectOf(hwnd, [parentPidl], shell.IID_IContextMenu,
                                                         0)  # <----- where i attempt to get menu for a drive.
        contextMenu_plus = None
        if contextMenu:
            # try to obtain a higher level pointer, first 3 then 2
            try:
                contextMenu_plus = contextMenu.QueryInterface(shell.IID_IContextMenu3, None)
            except Exception:
                try:
                    contextMenu_plus = contextMenu.QueryInterface(shell.IID_IContextMenu2, None)
                    print("plus", contextMenu_plus)
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
        MAX_SHELL_ID = 30000  #  30000

        contextMenu.QueryContextMenu(hMenu, 0, MIN_SHELL_ID, MAX_SHELL_ID, shellcon.CMF_EXPLORE)
                                     #  shellcon.CMF_CANRENAME)
        x, y = win32gui.GetCursorPos()
        flags = win32gui.TPM_LEFTALIGN | win32gui.TPM_RETURNCMD  # | win32gui.TPM_LEFTBUTTON | win32gui.TPM_RIGHTBUTTON
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
        # print("cmd", cmd - MIN_SHELL_ID)
        # print(contextMenu.GetCommandString(cmd - MIN_SHELL_ID, shellcon.GCS_UNICODE)) #shellcon.GCS_VERB))
        if cmd - MIN_SHELL_ID >= 0:
            # try:
            contextMenu.InvokeCommand(CI)
            # except:
            #     e = win32api.GetLastError()
            #     wx.LogError(win32api.FormatMessage(e))

    def get_context_menu2(self, path, file_names=[]):
        print(path, file_names)
        path = r'C:\temp'
        file_name = r'temp.txt'
        desktop_folder = shell.SHGetDesktopFolder()
        if not desktop_folder:
            raise Exception("Cannot get desktop folder")
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            raise Exception("Cannot get window handler")
        eaten, parent_pidl, attr = desktop_folder.ParseDisplayName(hwnd, None, path)
        if not parent_pidl:
            raise Exception("Cannot get parent pidl")
        parent_folder = desktop_folder.BindToObject(parent_pidl, None, shell.IID_IShellFolder)
        if not parent_folder:
            raise Exception("Cannot get parent folder")
        # if file_names:
        #     pidls = []
        #     for item in file_names:
        #         print(str(item))
        eaten, pidl, attr = parent_folder.ParseDisplayName(hwnd, None, file_name+"\0")
                # print(pidl)
                # if not pidl:
                #     raise Exception("Cannot get file pidl")
                # pidls.append(pidl)
        i, context_menu = parent_folder.GetUIObjectOf(hwnd, [pidl], shell.IID_IContextMenu, 0)
        context_menu = context_menu.QueryInterface(shell.IID_IContextMenu, None)
        # else:
        #     i, context_menu = desktop_folder.GetUIObjectOf(hwnd, [parent_pidl], shell.IID_IContextMenu, 0)
        if not context_menu:
            raise Exception("Cannot get context menu")
        menu = win32gui.CreatePopupMenu()
        if not menu:
            raise Exception("Cannot get menu")
        context_menu.QueryContextMenu(menu, 0, 1, 30000, shellcon.CMF_EXPLORE)
        x, y = win32gui.GetCursorPos()
        flags = win32gui.TPM_LEFTALIGN | win32gui.TPM_RETURNCMD
        cmd = win32gui.TrackPopupMenu(menu, flags, x, y, 0, hwnd, None)
        if cmd:
            ci = (0,  # Mask
                  hwnd,  # hwnd
                  cmd - 1,  # Verb
                  "",  # Parameters
                  "",  # Directory
                  win32con.SW_SHOWNORMAL,  # Show
                  0,  # HotKey
                  None  # Icon
                  )
            context_menu.InvokeCommand(ci)


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


CN_DUPL = "Duplicate this tab"
CN_LOCK = "Lock tab"
CN_LOCK_RENAME = "Rename/Lock tab"
CN_CLOSE_OTHERS = "Close other tabs"
CN_CLOSE = "Close tab"
CN_SEP = "-"


class TabMenu(wx.Menu):
    def __init__(self, frame, nb, tab_index):
        super().__init__()
        self.frame = frame
        self.nb = nb
        self.tab_index = tab_index
        self.menu_items = [(CN_DUPL, wx.ITEM_NORMAL), (CN_LOCK, wx.ITEM_CHECK), (CN_LOCK_RENAME, wx.ITEM_NORMAL),
                           (CN_CLOSE_OTHERS, wx.ITEM_NORMAL), ("-", wx.ITEM_SEPARATOR), (CN_CLOSE, wx.ITEM_NORMAL)]
        self.menu_items_id = {}
        for item in self.menu_items:
            self.menu_items_id[wx.NewId()] = item
        for id in self.menu_items_id.keys():
            item = self.Append(id, item=self.menu_items_id[id][0], kind=self.menu_items_id[id][1])
            if item.GetItemLabelText() == CN_LOCK and self.nb.conf[self.tab_index].locked:
                item.Check(True)
                if item.IsChecked():
                    print("checked")
                else:
                    print("not checked")
            self.Bind(wx.EVT_MENU, self.on_click, id=id)

    def on_click(self, event):
        operation = self.menu_items_id[event.GetId()][0]
        if operation == CN_DUPL:
            self.nb.duplicate_tab(self.tab_index)
        elif operation == CN_LOCK:
            if event.IsChecked():
                self.nb.lock_tab(tab_index=self.tab_index, tab_name=None)
            else:
                self.nb.unlock_tab(tab_index=self.tab_index)
        elif operation == CN_LOCK_RENAME:
            tab_name=self.nb.conf[self.tab_index].tab_name
            tab_name = tab_name[1:] if tab_name.startswith("*") else tab_name
            with dialogs.LockTabDlg(frame=self.frame,
                                    edit_text=tab_name) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    self.nb.lock_tab(tab_index=self.tab_index, tab_name=dlg.get_new_names()[0])
        elif operation == CN_CLOSE_OTHERS:
            for index in range(self.nb.GetPageCount() - 1, -1, -1):
                if index != self.tab_index:
                    self.nb.close_tab(index)
        elif operation == CN_CLOSE:
            self.nb.close_tab(self.tab_index)


class ShellShortcut:
    def __init__(self):
        self._base = pythoncom.CoCreateInstance(shell.CLSID_ShellLink,
                                                None,
                                                pythoncom.CLSCTX_INPROC_SERVER,
                                                shell.IID_IShellLink)

    def load(self, filename):
        self._base.QueryInterface(pythoncom.IID_IPersistFile).Load(filename)
        return self._base.GetPath(shell.SLGP_RAWPATH)[0]

    def save(self, filename):
        self._base.QueryInterface(pythoncom.IID_IPersistFile).Save(filename, 0)

    def __getattr__(self, name):
        if name != "_base":
            return getattr(self._base, name)



