import wx
from pathlib import Path
import util
import constants as cn
import path_pnl
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import filter_pnl
import time
import wx.aui as aui
import config
from pubsub import pub
import subprocess
import os
import dialogs
from lib4py import shell as sh
from code_viewer import high_code

CN_MAX_HIST_COUNT = 20


class Tit:
    def __init__(self, text):
        print(text)
        self.start = time.time()

    def __del__(self):
        print("Elapsed: ", time.time() - self.start)


class BrowserCtrl(aui.AuiNotebook):
    def __init__(self, parent, frame, im_list, conf, is_left):
        super().__init__(parent=parent, style=aui.AUI_NB_TAB_MOVE | # aui.AUI_NB_TAB_SPLIT |
                                              aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_TOP)
        self.SetArtProvider(aui.AuiDefaultTabArt())
        self.parent = parent
        self.frame = frame
        self.is_left = is_left
        self.im_list = im_list
        self.conf = conf
        self.begin_drag_index = None
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
        self.Bind(aui.EVT_AUINOTEBOOK_END_DRAG, self.on_end_drag)
        self.Bind(aui.EVT_AUINOTEBOOK_BEGIN_DRAG, self.on_begin_drag)
        self.Bind(wx.EVT_NAVIGATION_KEY, self.on_navigate)

    def on_navigate(self, e):
        if e.IsFromTab():
            if self.is_left:
                self.frame.go_to_right()
            else:
                self.frame.go_to_left()
        else:
            e.Skip()

    def on_child_focus(self, e):
        win = wx.Window.FindFocus()
        if isinstance(win, aui.AuiTabCtrl):
            self.on_page_changed(e)
        elif isinstance(win, Browser):
            pass
        elif isinstance(win, wx._core.ComboCtrl):
            if not self.get_active_browser().HasFocus():
                self.get_active_browser().SetFocus()
        else:
            # print(type(win))
            pass
        e.Skip()


    def on_begin_drag(self, e):
        self.begin_drag_index = e.GetSelection()

    def on_end_drag(self, e):
        new_index = e.GetSelection()
        self.conf[new_index], self.conf[self.begin_drag_index] = self.conf[self.begin_drag_index], self.conf[new_index]
        self.SetSelection(new_index)

    def on_tab_right_click(self, e):
        pt = wx.GetMousePosition()
        tab_index, flag = self.HitTest(self.ScreenToClient(pt))
        self.GetPage(self.GetSelection()).browser.SetFocus()
        menu = TabMenu(self.frame, self, tab_index)
        self.frame.PopupMenu(menu)
        del menu

    def on_ctrl_db_click(self, e):
        self.add_new_tab(self.get_active_browser().path)

    def add_tab(self, tab_conf, select=False):
        self.Freeze()
        tab = BrowserPnl(self, self.frame, self.im_list, tab_conf, self.is_left)
        self.AddPage(page=tab, caption=tab_conf.tab_name, select=select)
        self.Thaw()

    def add_new_tab(self, dir_name):
        tab_conf = config.BrowserConf()
        tab_conf.last_path = dir_name if dir_name else Path.home()
        self.conf.append(tab_conf)
        self.add_tab(tab_conf=tab_conf, select=True)

    def close_tab(self, tab_index):
        self.GetPage(tab_index).browser.unregister_listener(cn.CN_TOPIC_DIR_CHG)
        del self.conf[tab_index]
        self.DeletePage(tab_index)

    def duplicate_tab(self, tab_index):
        self.add_new_tab(dir_name=self.GetPage(tab_index).browser.path)

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

    def get_active_browser(self):
        return self.GetCurrentPage().browser


class BrowserPnl(wx.Panel):
    def __init__(self, parent, frame, im_list, tab_conf, is_left):
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame
        self.path_pnl = path_pnl.PathPanel(self, self.frame, is_left)
        self.browser = Browser(self, frame, im_list, tab_conf)
        self.filter_pnl = filter_pnl.FilterPnl(self, self.frame, self.browser)
        self.browser.set_references(self.path_pnl, self.filter_pnl)
        self.path_pnl.hist_menu.set_browser(self.browser)
        self.browser.open_dir(tab_conf.last_path)
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
        self.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.on_start_drag, id=self.win_id)
        self.register_listener(topic=cn.CN_TOPIC_DIR_CHG)

    def on_process_dropped_files(self, x, y, file_names):
        src_id = self.drag_src.win_id if self.drag_src else -1
        tgt_id = self.drag_tgt.object.win_id
        same_win = src_id == tgt_id
        item, flags = self.HitTest((x, y))
        if same_win:
            self.frame.move([f for f in file_names if Path(f).is_dir()],
                            [f for f in file_names if Path(f).is_file()],
                            self.path.joinpath(self.GetItemText(item)))
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
        if self.path.exists():
            os.chdir(str(self.path))
            self.path_pnl.path_lbl._refresh()
            # self.frame.get_inactive_win().get_active_browser().path_pnl.path_lbl.Refresh()
        else:
            self.open_directory(str(self.get_next_dir(self.path)), cn.CN_GO_BACK, self.conf)
        e.Skip()

    def on_kill_focus(self, e):
        self.path_pnl.path_lbl.reset()
        e.Skip()

    def __repr__(self):
        return str(self.path)

    def register_listener(self, topic):
        if not pub.subscribe(self.listen_dir_changes, topic):
            raise Exception("Cannot register watchdir listener")

    def unregister_listener(self, topic):
        if not pub.unsubscribe(self.listen_dir_changes, topic):
            raise Exception("Cannot unregister watchdir listener")

    def listen_dir_changes(self, dir_name, added, deleted):
        if str(self.path) == str(dir_name):
            self.refresh_list(dir_name=dir_name, conf=self.conf, to_select=[], reread_source=True)

    def get_source_id_in_list(self, item_name):
        print("cache before delete", [item[cn.CN_COL_NAME] for item in self.dir_cache])
        index = [item[cn.CN_COL_NAME] for item in self.dir_cache].index(item_name)
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
            if 0 <= item < len(self.dir_cache):
                if col == cn.CN_COL_DATE:
                    return util.format_date(self.dir_cache[item][col])
                elif col == cn.CN_COL_SIZE:
                    return util.format_size(self.dir_cache[item][col])
                else:
                    return self.dir_cache[item][col]
            else:
                return ""

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
        if item > len(self.dir_cache):
            return -1
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
            self.filter_pnl.enable_filter()
        e.Skip()

    def show_hide_cols(self, column_conf):
        for col in column_conf.keys():
            if column_conf[col]:
                self.SetColumnWidth(col + 1, 105)
            else:
                self.SetColumnWidth(col + 1, 0)

    def on_col_right_click(self, event):
        menu = ColumnMenu(self, event.GetColumn())
        self.frame.PopupMenu(menu)
        del menu

    def add_hist_item(self, path):
        if path not in self.history:
            self.history.insert(0, path)
            if len(self.history) > self.frame.app_conf.history_limit:
                self.history.pop()

    def on_select(self, event):
        self.update_summary_lbl()
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
                    return True
        return False


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
        print("set_selection", selected)
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
                sh.get_context_menu(str(self.path), [])
            else:
                items = self.get_selected()
                # items = [str(self.path.joinpath(item)) for item in self.get_selected()]
                sh.get_context_menu(str(self.path), self.get_selected())

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
        self.set_tab_name(self.conf.tab_name)
        self.path_pnl.set_value(str(value))
        self.add_hist_item(str(value))
        self.root = value.samefile(value.anchor)
        self._path = value

    def do_search_folder(self, pattern):
        hist = pattern
        if not pattern:
            pattern = ["*"]
        else:
            pattern = list(map(lambda x: "*" + x + "*",
                               [part.strip() for part in pattern.split(";") if part.strip()]))
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
                lnk = sh.Shortcut()
                res = lnk.load(str(new_path))
                new_path = Path(res)
                del lnk
            if new_path.is_file():
                sh.start_file(new_path)
                self.frame.show_wait()
            elif new_path.is_dir():
                if wx.GetKeyState(wx.WXK_CONTROL) and wx.GetKeyState(wx.WXK_SHIFT):
                    self.frame.get_inactive_win().add_new_tab(new_path)
                elif wx.GetKeyState(wx.WXK_CONTROL):
                    self.page_ctrl.add_new_tab(new_path)
                else:
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
        bmp = sh.extension_to_bitmap(extension)
        index = self.image_list.Add(bmp)
        self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)
        self.extension_images[extension] = index
        return index

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
            if str(self.path) == str(dir_name):
                # to_select = self.get_selected()
                to_select = [sel_dir] if sel_dir else self.get_selected()
            else:
                self.filter_pnl.disable_filter(clear_search=False, search_pattern=False)
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
            self.open_dir(temp)

    def refresh_list(self, dir_name, conf, to_select, reread_source=False):
        self.dir_cache = self.frame.dir_cache.get_dir(dir_name=Path(dir_name), conf=conf, reread_source=reread_source)
        self.path = Path(dir_name)
        count = len(self.dir_cache)
        if not self.root:
            count += 1
        self.SetItemCount(count)
        if count:
            self.Refresh()
            self.set_selection(to_select)
        else:
            self.DeleteAllItems()
        self.update_summary_lbl()

    def shell_viewer(self, folders, files):
        if len(files) > 0:
            self.frame.vim.show_files(file_names=[str(f) for f in files])
        else:
            self.frame.show_message(cn.CN_NO_ITEMS_SEL)
        # args = ["pythonw", str(cn.CN_VIEWER_APP), "-r"]
        # if files:
        #     args.extend([str(f) for f in files])
        #     subprocess.Popen(args, shell=False, cwd=cn.CN_VIEWER_APP.parent)
        # elif folders:
        #     if len(folders) == 1:
        #         self.frame.show_message("Show folder properties")
        #     else:
        #         self.frame.show_message("Selected one folder")
        # else:
        #     self.frame.show_message(cn.CN_NO_ITEMS_SEL)


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
CN_DUPL_OW = "Duplicate this tab in opposite window"
CN_LOCK = "Lock tab"
CN_LOCK_RENAME = "Rename/Lock tab"
CN_CLOSE_DUPL = "Close duplicated tabs"
CN_CLOSE_OTHERS = "Close all other tabs"
CN_CLOSE = "Close tab"
CN_SEP = "-"


class TabMenu(wx.Menu):
    def __init__(self, frame, nb, tab_index):
        super().__init__()
        self.frame = frame
        self.nb = nb
        self.tab_index = tab_index
        self.menu_items = [(CN_DUPL, wx.ITEM_NORMAL), (CN_DUPL_OW, wx.ITEM_NORMAL), (CN_SEP, wx.ITEM_SEPARATOR),
                           (CN_LOCK, wx.ITEM_CHECK), (CN_LOCK_RENAME, wx.ITEM_NORMAL), (CN_SEP, wx.ITEM_SEPARATOR),
                           (CN_CLOSE_DUPL, wx.ITEM_NORMAL), (CN_CLOSE_OTHERS, wx.ITEM_NORMAL),
                           (CN_CLOSE, wx.ITEM_NORMAL)]
        self.menu_items_id = {}
        for item in self.menu_items:
            self.menu_items_id[wx.NewId()] = item
        for id in self.menu_items_id.keys():
            item = self.Append(id, item=self.menu_items_id[id][0], kind=self.menu_items_id[id][1])
            if item.GetItemLabelText() == CN_LOCK and self.nb.conf[self.tab_index].locked:
                item.Check(True)
            self.Bind(wx.EVT_MENU, self.on_click, id=id)

    def on_click(self, event):
        operation = self.menu_items_id[event.GetId()][0]
        if operation == CN_DUPL:
            self.nb.duplicate_tab(self.tab_index)
        elif operation == CN_DUPL_OW:
            self.frame.get_inactive_win().add_new_tab(dir_name=self.nb.GetPage(self.tab_index).browser.path)
        elif operation == CN_LOCK:
            if event.IsChecked():
                self.nb.lock_tab(tab_index=self.tab_index, tab_name=None)
            else:
                self.nb.unlock_tab(tab_index=self.tab_index)
        elif operation == CN_LOCK_RENAME:
            tab_name = self.nb.conf[self.tab_index].tab_name
            tab_name = tab_name[1:] if tab_name.startswith("*") else tab_name
            with dialogs.LockTabDlg(frame=self.frame,
                                    edit_text=tab_name) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    self.nb.lock_tab(tab_index=self.tab_index, tab_name=dlg.get_new_names()[0])
        elif operation == CN_CLOSE_DUPL:
            ids = []
            visited = []
            for index in range(self.nb.GetPageCount() - 1):
                ids.append((index, self.nb.GetPage(index).browser.win_id,
                            str(self.nb.GetPage(index).browser.path)))
            for tab_index, id, path in ids:
                if path not in visited:
                    for index in range(self.nb.GetPageCount() - 1, tab_index, -1):
                        if self.nb.GetPage(index).browser.win_id != id and \
                                str(self.nb.GetPage(index).browser.path) == path:
                            self.nb.close_tab(index)
                        visited.append(path)
        elif operation == CN_CLOSE_OTHERS:
            win_id = self.nb.GetPage(self.tab_index).browser.win_id
            for index in range(self.nb.GetPageCount() - 1, -1, -1):
                if self.nb.GetPage(index).browser.win_id != win_id:
                    self.nb.close_tab(index)
        elif operation == CN_CLOSE:
            self.nb.close_tab(self.tab_index)






