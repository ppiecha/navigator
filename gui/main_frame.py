import subprocess

import win32con
import wx
from gui import browser
from gui import history
from gui import menu
from util import util as util, constants as cn
from gui import config
import pickle
import os
from pathlib import Path
import wx.aui as aui
from gui import dialogs
import traceback
import wx.adv
import sys
from datetime import datetime
from typing import List
from lib4py import shell as sh
from lib4py import logger as lg
from code_viewer import viewer
from finder import main_frame as finder
from gui.controls import CmdBtn
from pubsub import pub
import logging
from gui import clip
from util.com_type import HotKey
from util.dir_watcher import DirCache

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title=cn.CN_APP_NAME, size=(600, 500), style=wx.DEFAULT_FRAME_STYLE)
        self.app_conf: config.NavigatorConf = config.NavigatorConf()
        self.menu_bar = menu.MainMenu(self)
        self.SetMenuBar(self.menu_bar)
        self.dir_cache = DirCache(self)
        self.thread_lst = []
        self.SetIcon(wx.Icon(cn.CN_ICON_FILE_NAME))
        self.im_list = wx.ImageList(16, 16)
        self.extension_images = {}
        self.sizer = None
        self.wait = None
        self.last_active_browser = None

        self.InitUI()
        self.process_args()

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.vim = viewer.MainFrame(nav_frame=self)
        self.finder = finder.MainFrame(app=wx.GetApp(), nav_frame=self)
        self.clip_view = clip.ClipFrame(main_frame=self)
        self.items_history = None

    def refresh_lists(self):
        if self.items_history:
            self.items_history.refresh_lists()

    def go_to_left(self):
        self.left_browser.get_active_browser().SetFocus()

    def go_to_right(self):
        self.right_browser.get_active_browser().SetFocus()

    def process_args(self):
        if len(sys.argv) > 1:
            opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
            args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
            if "-w" in opts:
                sys.excepthook = self.except_hook
        else:
            pass

    def except_hook(self, type, value, tb):
        message = ''.join(traceback.format_exception(type, value, tb))
        self.append_log(message)
        wx.LogError(message)

    def append_log(self, log):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        txt = []
        txt.append("-----------------------------------------------------------------------------\n")
        txt.append(current_time + "\n")
        txt.append("-----------------------------------------------------------------------------\n")
        txt.append(log + "\n")
        with open(cn.CN_APP_LOG, "a+") as f:
            f.writelines(txt)
            f.close()

    def get_active_win(self):
        self.return_focus()
        win = self.FindFocus()
        if isinstance(win, browser.Browser):
            return win.page_ctrl
        else:
            print(type(win))
            raise Exception("Cannot find active page ctrl")

    def get_inactive_win(self):
        self.return_focus()
        win = self.FindFocus()
        if isinstance(win, browser.Browser):
            if win.page_ctrl.is_left:
                return self.right_browser
            else:
                return self.left_browser
        else:
            raise Exception("active " + str(type(win)))

    def return_focus(self):
        self.last_active_browser.SetFocus()
        # self.SetFocus()
        # self.splitter.SetFocus()

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
            with open(conf_file, 'wb') as ac:
                pickle.dump(app_conf, ac)
        except IOError:
            self.log_error("Cannot save project file '%s'." % conf_file)

    def get_ext_image_id(self, extension):
        """Get the id in the image list for the extension.
        Will add the image if not there already"""
        # Caching
        if extension in self.extension_images:
            return self.extension_images[extension]
        bmp = sh.extension_to_bitmap(extension)
        index = self.im_list.Add(bmp)
        # self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)
        self.extension_images[extension] = index
        return index

    def InitUI(self):

        self.Freeze()

        self.app_conf = self.read_last_conf(cn.CN_APP_CONFIG, self.app_conf)
        self.app_conf.update_history(self.thread_lst)

        # Menu
        self.menu_bar.menu_items_id[cn.ID_SHOW_HIDDEN].Check(self.app_conf.show_hidden)

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
        self.img_user = self.im_list.Add(wx.Bitmap(cn.CN_IM_USER, wx.BITMAP_TYPE_PNG))
        self.img_parent = self.im_list.Add(wx.Bitmap(cn.CN_IM_PARENT, wx.BITMAP_TYPE_PNG))
        self.img_child = self.im_list.Add(wx.Bitmap(cn.CN_IM_CHILD, wx.BITMAP_TYPE_PNG))
        # self.img_link_folder = self.im_list.Add(wx.Bitmap(cn.CN_IM_NEW_FOLDER, wx.BITMAP_TYPE_PNG))
        self.img_clip = self.im_list.Add(wx.Bitmap(cn.CN_IM_NEW_FILE, wx.BITMAP_TYPE_PNG))
        # self.img_link = self.im_list.Add(wx.Bitmap(cn.CN_IM_LINK, wx.BITMAP_TYPE_PNG))
        # self.img_link_shortcut = self.im_list.Add(wx.Bitmap(cn.CN_IM_SHORTCUT, wx.BITMAP_TYPE_PNG))

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
        buttons = [CmdBtn(self, cn.ID_RENAME, "F2 Rename", size=btn_size),
                   CmdBtn(self, cn.ID_VIEW, "F3 View", size=btn_size),
                   CmdBtn(self, cn.ID_EDIT, "F4 Edit", size=btn_size),
                   CmdBtn(self, cn.ID_COPY, "F5 Copy", size=btn_size),
                   CmdBtn(self, cn.ID_MOVE, "F6 Move", size=btn_size),
                   CmdBtn(self, cn.ID_NEW_FOLDER, "F7 Mkdir", size=btn_size),
                   CmdBtn(self, cn.ID_DELETE, "F8 Delete", size=btn_size),
                   CmdBtn(self, cn.ID_NEW_FILE, "F9 Mkfile", size=btn_size)]

        for btn in buttons:
            self.btn_sizer.Add(btn, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
            # btn.Bind(wx.EVT_BUTTON, self.menu_bar.on_click, id=btn.GetId())

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitter, proportion=1, flag=wx.EXPAND)
        self.sizer.Add(self.btn_sizer, proportion=0, flag=wx.EXPAND)

        self.SetSizer(self.sizer)
        # self.SetMinSize(self.GetEffectiveMinSize())

        if self.app_conf.nav_rect:
            self.SetRect(self.app_conf.nav_rect)
        else:
            self.SetSize((700, 500))
            self.Center()

        self.SetDefaultItem(self.left_browser)
        self.Thaw()
        self.left_browser.get_active_browser().SetFocus()

        mod_key = win32con.MOD_WIN | win32con.MOD_ALT

        self.register_hot_key(hot_key=HotKey(id=cn.ID_HOT_KEY_SHOW, mod_key=mod_key,
                                             key=win32con.VK_RETURN, action=self.show_hide_main_frame))

        self.register_hot_key(hot_key=HotKey(id=cn.ID_HOT_KEY_SHOW_CLIP, mod_key=mod_key,
                                             key=win32con.VK_UP, action=self.show_hide_clip))

        self.register_hot_key(hot_key=HotKey(id=cn.ID_HOT_KEY_CLIP_URL, mod_key=mod_key,
                                             key=win32con.VK_DOWN, action=self.open_clip_url))

        self.register_hot_key(hot_key=HotKey(id=cn.ID_HOT_KEY_LEFT_URL, mod_key=mod_key,
                                             key=win32con.VK_LEFT, action=self.open_left_url))

    def register_hot_key(self, hot_key: HotKey) -> None:
        ok = self.RegisterHotKey(hotkeyId=hot_key.id,  # a unique ID for this hotkey
                                 modifiers=hot_key.mod_key,  # win32con.MOD_WIN,  # the modifier key
                                 virtualKeyCode=hot_key.key)  # win32con.VK_SPACE)  # the key to watch for
        if not ok:
            self.show_message(f"Cannot register hot key under number {hot_key.id}")
        else:
            self.Bind(wx.EVT_HOTKEY, hot_key.action, id=hot_key.id)

    def open_left_url(self, e):
        util.open_url(self.app_conf.url_left)

    def open_clip_url(self, e):
        util.open_clip_url()

    def show_hide_wnd(self, wnd: wx.Frame):
        def raise_wnd():
            if not wnd.IsShown():
                wnd.Show()
            wnd.Raise()

        if wnd.IsIconized():
            wnd.Iconize(False)
            raise_wnd()
        else:
            if wnd.IsActive():
                if wnd is self:
                    wnd.Iconize(True)
                else:
                    wnd.Hide()
            else:
                raise_wnd()

    def show_hide_clip(self, e):
        self.show_hide_wnd(wnd=self.clip_view)

    def show_hide_main_frame(self, e):
        self.show_hide_wnd(wnd=self)

    def on_size(self, e):
        size = self.GetSize()
        self.splitter.SetSashPosition(size.x / 2)
        e.Skip()

    def on_db_click(self, e):
        size = self.GetSize()
        self.splitter.SetSashPosition(size.x / 2)

    def on_close(self, event):
        self.app_conf.nav_rect = self.GetRect()
        self.app_conf.vim_rect = self.vim.GetRect()
        self.app_conf.find_res_rect = self.finder.res_frame.GetRect()
        self.app_conf.finder_rect = self.finder.GetRect()
        self.app_conf.clip_view_rect = self.clip_view.GetRect()
        self.vim.Destroy()
        self.finder.res_frame.Destroy()
        self.finder.Destroy()
        if hasattr(self, 'sql_nav'):
            self.sql_nav.Destroy()
        self.clip_view.Destroy()
        if self.items_history:
            self.items_history.Destroy()
        self.write_last_conf(cn.CN_APP_CONFIG, self.app_conf)
        if not self.release_resources():
            event.Veto()
            return
        if not self.UnregisterHotKey(cn.ID_HOT_KEY_SHOW):
            self.show_message(f"Cannot unregister hot key {cn.ID_HOT_KEY_SHOW}")
        if not self.UnregisterHotKey(cn.ID_HOT_KEY_SHOW_CLIP):
            self.show_message(f"Cannot unregister hot key {cn.ID_HOT_KEY_SHOW_CLIP}")
        event.Skip()

    def show_message(self, text):
        dlg = wx.MessageDialog(self, text, caption=cn.CN_APP_NAME)
        # dlg = wx.MessageBox(text, caption=cn.CN_APP_NAME)
        # dlg = dialogs.messageDialog(parent=self, message=text, title=cn.CN_APP_NAME)
        # dlg = dialogs.findDialog(parent=self, searchText='text to find', wholeWordsOnly=0, caseSensitive=0)
        dlg.ShowModal()

    def get_question_feedback(self, question, caption=cn.CN_APP_NAME, parent: wx.Window = None):
        dlg = wx.MessageDialog(parent=parent if parent else self,
                               message=question,
                               style=wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION,
                               caption=caption)
        return dlg.ShowModal()

    def show_wait(self):
        self.wait = wx.BusyCursor(cursor=wx.Cursor(wx.CURSOR_ARROWWAIT))
        wx.CallLater(200, self.hide_wait)

    def hide_wait(self):
        del self.wait

    def log_error(self, message):
        # wx.LogError(message)
        self.show_message(message)

    def release_resources(self):
        for th in self.thread_lst:
            if th.is_alive():
                self.show_message("Some background tasks are running still")
                return False
        self.Hide()
        self.dir_cache.release_resources()
        del self.im_list
        return True

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
                    util.run_in_thread(target=sh.rename,
                                       args=(os.path.join(b.path, old_name),
                                             os.path.join(b.path, dlg.get_new_names()[0]),
                                             dlg.cb_rename.IsChecked()),
                                       lst=self.thread_lst)

    def view(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        b.shell_viewer(folders, files)

    def edit(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        b.shell_editor(files)

    def compare_files(self):
        self.return_focus()
        win = self.get_active_win()
        reverse = not win.is_left
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        if len(files) == 0:
            self.show_message(cn.CN_NO_ITEMS_SEL)
        elif len(files) == 1:
            win = self.get_inactive_win()
            b = win.get_active_browser()
            folders2, files2 = b.get_selected_files_folders()
            if len(files2) == 0:
                self.show_message("Select file to compare")
            elif len(files2) == 1:
                files = files + files2
                if reverse:
                    files.reverse()
                b.compare_files(files)
            else:
                self.show_message("More than two files selected")
        elif len(files) == 2:
            if reverse:
                files.reverse()
            b.compare_files(files)
        else:
            self.show_message("More than two files selected")

    def copy_text2clip(self, lst):
        if wx.TheClipboard.Open():
            text = "\n".join(lst)
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
        else:
            self.show_message("Cannot copy text to clipboard")

    def copy_file2clip(self, e):
        win = self.get_active_win()
        b = win.get_active_browser()
        path = b.path
        lst = [str(path.joinpath(b)) for b in b.get_selected()]
        if lst:
            if wx.TheClipboard.Open():
                data = util.FileDataObject(nav_frame=self)
                for item in lst:
                    data.add_file(file=item)
                wx.TheClipboard.SetData(data)
                wx.TheClipboard.Close()
                self.show_wait()
            else:
                self.show_message("Cannot copy selected items")

    def paste_files_from_clip(self, e):
        win = self.get_active_win()
        b = win.get_active_browser()
        path = b.path
        util.run_in_thread(sh.paste_file, [path], lst=self.thread_lst)
        self.show_wait()
        # self.paste_file(path)
        # if wx.TheClipboard.Open():
        #     data = wx.FileDataObject()
        #     success = wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_FILENAME))
        #     if success:
        #         success = wx.TheClipboard.GetData(data)
        #         if not success:
        #             self.show_message("Cannot paste from clipboard")
        #         else:
        #             lst = data.GetFilenames()
        #             print(lst)
        #     wx.TheClipboard.Close()

    def copy(self, folders: List[str] = None, files: List[str] = None, dst_path="") -> None:
        win = self.get_active_win()
        b = win.get_active_browser()
        if folders is not None or files is not None:
            if folders:
                path = Path(folders[0]).parent
            else:
                path = Path(files[0]).parent
            dst = dst_path
        else:
            path = b.path
            _folders, _files = b.get_selected_files_folders()
            folders = [str(f) for f in _folders]
            files = [str(f) for f in _files]
            inactive = self.get_inactive_win()
            dst = str(inactive.get_active_browser().path)
        if folders or files:
            opr_count, src, dst = self.get_oper_details(prefix="Copy ", folders=folders,
                                                        files=files, source_path=path,
                                                        dest_path=dst,
                                                        oper_id=cn.ID_COPY)
            with dialogs.CopyMoveDlg(self, title="Copy", opr_count=opr_count, src=src, dst=dst) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    dst_dir, dst_name = dlg.get_path_and_name()
                    if not dst_name:
                        util.run_in_thread(target=sh.copy,
                                           args=(folders + files, str(dst_dir), dlg.cb_rename.IsChecked()),
                                           lst=self.thread_lst)
                    else:
                        util.run_in_thread(target=sh.copy_file,
                                           args=(str(path.joinpath(sh.get_file_name(files[0]))),
                                                 str(dst_dir.joinpath(dst_name)),
                                                 dlg.cb_rename.IsChecked()),
                                           lst=self.thread_lst)
        else:
            self.show_message(cn.CN_NO_ITEMS_SEL)

    def move(self, folders: List[str] = None, files: List[str] = None, dst_path: str = "") -> None:
        win = self.get_active_win()
        b = win.get_active_browser()
        if folders is not None or files is not None:
            if folders:
                path = Path(folders[0]).parent
            else:
                path = Path(files[0]).parent
            dst = dst_path
        else:
            path = b.path
            _folders, _files = b.get_selected_files_folders()
            folders = [str(f) for f in _folders]
            files = [str(f) for f in _files]
            inactive = self.get_inactive_win()
            dst = str(inactive.get_active_browser().path)
        if folders or files:
            opr_count, src, dst = self.get_oper_details(prefix="Move ", folders=folders,
                                                        files=files, source_path=path,
                                                        dest_path=dst,
                                                        oper_id=cn.ID_MOVE)
            with dialogs.CopyMoveDlg(self, title="Move", opr_count=opr_count, src=src, dst=dst) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    dst_dir, dst_name = dlg.get_path_and_name()
                    if not dst_name:
                        util.run_in_thread(target=sh.move,
                                           args=(folders + files, str(dst_dir), dlg.cb_rename.IsChecked()),
                                           lst=self.thread_lst)
                    else:
                        util.run_in_thread(target=sh.move_file,
                                           args=(str(path.joinpath(sh.get_file_name(files[0]))),
                                                 str(dst_dir.joinpath(dst_name)),
                                                 dlg.cb_rename.IsChecked()),
                                           lst=self.thread_lst)
        else:
            self.show_message(cn.CN_NO_ITEMS_SEL)

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
                            try:
                                sh.new_folder(str(path))
                            except Exception as e:
                                self.log_error(f"Cannot create folder {path.name}\n{str(e)}")

    def delete(self, e):
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
                if wx.GetKeyState(wx.WXK_CONTROL):
                    dlg.cb_perm.SetValue(wx.CHK_CHECKED)
                if dlg.show_modal() == wx.ID_OK:
                    util.run_in_thread(target=sh.delete,
                                       args=(folders + files, dlg.cb_perm.IsChecked()),
                                       lst=self.thread_lst)
        else:
            self.show_message(cn.CN_NO_ITEMS_SEL)

    def new_file(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        def_name = files[0].name if files else "new_file.sql"
        with dialogs.NewFileDlg(self, b.path, def_name) as dlg:
            if dlg.show_modal() == wx.ID_OK:
                file_names = dlg.get_new_names()
                print(Path(file_names[0]).parts)
                for f in file_names:
                    file_path = b.path.joinpath(f)
                    path: Path = b.path
                    for part in file_path.parts:
                        path = path.joinpath(part.rstrip())
                        if not path.exists():
                            print("adding", str(path))
                            if path.name == path.stem:
                                try:
                                    sh.new_folder(str(path))
                                except Exception as e:
                                    self.log_error(f"Cannot create folder {path.name}\n{str(e)}")
                            else:
                                try:
                                    sh.new_file(str(path))
                                except Exception as e:
                                    self.log_error(f"Cannot create file {path.name}\n{str(e)}")
                    if dlg.cb_open.IsChecked():
                        sh.start_file(str(path))


    def new_file_from_clip(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        def_name = files[0].name if files else "new_file.sql"
        with dialogs.NewFileDlg(self, b.path, def_name, validate_files=False) as dlg:
            if dlg.show_modal() == wx.ID_OK:
                file_names = dlg.get_new_names()
                for f in file_names:
                    path = b.path.joinpath(f)
                    if Path(path).exists():
                        if self.get_question_feedback("Overwrite?") in (wx.NO, wx.CANCEL):
                            return
                    try:
                        if not wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                            self.show_message("No text data in clipboard")
                            return
                        with open(path, 'w') as file:
                            try:
                                text_data = wx.TextDataObject()
                                if wx.TheClipboard.Open():
                                    success = wx.TheClipboard.GetData(text_data)
                                    wx.TheClipboard.Close()
                                if success:
                                    file.write(text_data.GetText())
                                else:
                                    self.show_message("Cannot get text data from clipboard")
                            except Exception as e:
                                self.show_message(f"Cannot write clipboard text data to file \n{path} \n{str(e)}")
                    except Exception as e:
                        self.log_error(f"Cannot create file {path.name}\n{str(e)}")
                    if dlg.cb_open.IsChecked():
                        sh.start_file(str(path))

    def get_oper_details(self, prefix: str, folders: List[str], files: List[str], source_path: str, dest_path: str,
                         oper_id: int):
        all = folders + files
        dest_dir = Path(dest_path)
        src_dir = Path(source_path)
        src = "From: " + str(src_dir) + " to"
        if len(all) == 0:
            name = src_dir.name
            opr_count = prefix + str(name)
            dst = str(dest_dir.joinpath(name)) + ".lnk"
        elif len(all) == 1:
            full_name = Path(all[0])
            name = full_name.name
            stem = full_name.stem
            opr_count = prefix + str(name)
            if oper_id == cn.ID_CREATE_SHORTCUT:
                dst = str(dest_dir.joinpath(name)) + ".lnk"
            elif oper_id == cn.ID_COPY2SAME:
                dst = str(src_dir.joinpath(name))
            elif oper_id in (cn.ID_COPY, cn.ID_MOVE) and full_name.is_file():
                dst = str(dest_dir.joinpath(name))
            else:
                dst = str(dest_path)
        else:
            opr_desc = ""
            if folders:
                opr_desc = str(len(folders)) + " folder(s)"
                if files:
                    opr_desc += " and " + str(len(files)) + " file(s)"
            elif files:
                opr_desc = str(len(files)) + " file(s)"
            opr_count = prefix + opr_desc
            dst = str(dest_path)

        return opr_count, src, dst

    def on_create_shortcut(self, e):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        opr_count, src, dst = self.get_oper_details(prefix="Create shortcut(s) for ", folders=folders,
                                                    files=files, source_path=b.path,
                                                    dest_path=self.get_inactive_win().get_active_browser().path,
                                                    oper_id=cn.ID_CREATE_SHORTCUT)
        with dialogs.CopyMoveDlg(self,
                                 title="Create shortcut(s)",
                                 opr_count=opr_count,
                                 src=src,
                                 dst=dst,
                                 show_cb=False) as dlg:
            if dlg.show_modal() == wx.ID_OK:
                path, name = dlg.get_path_and_name()
                if len(folders + files) > 0:
                    for f in folders:
                        sh.Shortcut.new_shortcut(path=path,
                                                 lnk_name=name if name else f.name + ".lnk",
                                                 target=os.path.join(b.path, f.name))
                    for f in files:
                        sh.Shortcut.new_shortcut(path=path,
                                                 lnk_name=name if name else f.name + ".lnk",
                                                 target=os.path.join(b.path, f.name))
                else:
                    sh.Shortcut.new_shortcut(path=path,
                                             lnk_name=name,
                                             target=os.path.join(b.path, ""))

    def on_copy2same(self, e):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        sel_count = len(folders + files)
        if sel_count == 0:
            self.show_message(cn.CN_NO_ITEMS_SEL)
        elif sel_count > 1:
            self.show_message("Select only one item")
        else:
            def_name = files[0].name if files else folders[0].name
            item_type = "file" if files else "folder"
            with dialogs.NewItemDlg(self, "Copy to the same folder", b.path, def_name,
                                    label=f"Enter {item_type} name where to copy") as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    new_name = dlg.get_new_names()[0]
                    full_name = b.path.joinpath(new_name)
                    if item_type == "file":
                        util.run_in_thread(target=sh.copy_file,
                                           args=(str(b.path.joinpath(files[0].name)),
                                                 str(full_name), 0),
                                           lst=self.thread_lst)
                    else:
                        try:
                            sh.new_folder(str(full_name))
                        except Exception as e:
                            self.log_error(f"Cannot create folder {new_name}\n{str(e)}")
                        else:
                            util.run_in_thread(target=sh.copy,
                                               args=[str(b.path.joinpath(str(folders[0]), "*.*")),
                                                     str(full_name)],
                                               lst=self.thread_lst)

    def select_all(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        b.select_all()

    def invert_selection(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        b.invert_selection()

    def copy_sel2clip(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        self.copy_text2clip(b.get_selected())

    def copy_sel2clip_with_path(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        self.copy_text2clip([str(f) for f in folders] + [str(f) for f in files])

    def copy_file_content_to_clip(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        folders, files = b.get_selected_files_folders()
        b.copy_file_content_to_clip(files=files)

    def target_eq_source(self):
        if str(self.get_inactive_win().get_active_browser().path) != \
                str(self.get_active_win().get_active_browser().path):
            self.get_inactive_win().get_active_browser().open_dir(
                self.get_active_win().get_active_browser().path)

    def swap_wins(self):
        act = self.get_active_win().get_active_browser().path
        in_act = self.get_inactive_win().get_active_browser().path
        if str(act) != str(in_act):
            self.get_active_win().get_active_browser().open_dir(in_act)
            self.get_inactive_win().get_active_browser().open_dir(act)

    def _search(self, path="", words=[]):
        self.finder.re_init()
        self.finder.show(search_path=path)
        # args = ["pythonw", str(cn.CN_FINDER_APP), str(path)]
        # subprocess.Popen(args, shell=False, cwd=cn.CN_FINDER_APP.parent)

    def search(self):
        self._search(self.get_active_win().get_active_browser().path)

    def reread_source(self):
        act = self.get_active_win().get_active_browser()
        act.reread(dir_name=str(act.path))

    def show_hidden(self):
        self.app_conf.show_hidden = self.menu_bar.menu_items_id[cn.ID_SHOW_HIDDEN].IsChecked()
        self.dir_cache.refresh()
        pub.sendMessage(cn.CN_TOPIC_REREAD)

    def run_command_prompt(self):
        win = self.get_active_win()
        b = win.get_active_browser()
        selected_path = b.path
        if not selected_path:
            self.show_message(f"Cannot determine selected path")
        curr_path = os.getcwd()
        os.chdir(selected_path)
        subprocess.Popen(["start", "cmd"], shell=True)
        os.chdir(curr_path)

    def history(self):
        if not self.items_history:
            self.items_history = history.LinkDlg(self, is_left=self.get_active_win().is_left, is_read_only=True)
        self.items_history.refresh_lists()
        self.items_history.show()
        self.items_history.SetFocus()

    def show_options(self, active_page):
        with dialogs.OptionsDlg(frame=self, active_page=active_page) as dlg:
            ret = dlg.show_modal()
            del dlg
            return ret

