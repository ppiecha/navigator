import subprocess

import wx
import wx.html2
import wx.aui as aui
from pathlib import Path
from util import util as util, constants as cn, util_file
from code_viewer import high_code
from lib4py import logger as lg
import logging
logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)

ID_FIND_NEXT = wx.NewId()
ID_FIND_PREV = wx.NewId()
ID_EDIT = wx.NewId()


class ViewerCtrl(aui.AuiNotebook):
    def __init__(self, viewer_frame):
        super().__init__(parent=viewer_frame, style=aui.AUI_NB_CLOSE_ON_ALL_TABS | aui.AUI_NB_SCROLL_BUTTONS |
                                                    aui.AUI_NB_TOP | aui.AUI_NB_WINDOWLIST_BUTTON)
        self.viewer_frame = viewer_frame
        self.Bind(wx.EVT_CHILD_FOCUS, self.on_child_focus)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.page_close)
        self.Bind(aui.EVT_AUINOTEBOOK_BEGIN_DRAG, self.on_start_drag)

    def page_close(self, e):
        pt = wx.GetMousePosition()
        tab_index, flag = self.HitTest(self.ScreenToClient(pt))
        logger.debug(f"page close tab index {tab_index}")
        page = self.GetPage(tab_index)
        page.browser.drop_file()

    def on_child_focus(self, e):
        index = self.GetSelection()
        if index == -1:
            return
        page = self.GetPage(index)
        logger.debug(f"active file {page.file_name}")
        if page.to_be_reloaded(page.file_name) == wx.ID_YES:
            page.browser.reload(reread=True)
        self.viewer_frame.set_caption()
        logger.debug(f"focus goes to {type(e)} {type(wx.Window.FindFocus())}")
        e.Skip()

    def on_start_drag(self, e):
        selected = self.viewer_frame.get_active_page().browser.get_file_name()
        if not selected:
            return
        files = util_file.FileDataObject(nav_frame=self.viewer_frame.nav_frame)
        files.add_file(file=selected)
        drag_src = wx.DropSource(win=self, data=files)
        result = drag_src.DoDragDrop()


class MainFrame(wx.Frame):
    def __init__(self, nav_frame):
        super().__init__(parent=nav_frame, title=cn.CN_APP_NAME_VIEWER, size=(800, 600), style=wx.DEFAULT_FRAME_STYLE)
        self.page_ctrl = ViewerCtrl(viewer_frame=self)
        self.nav_frame = nav_frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.page_ctrl, flag=wx.EXPAND, proportion=1)
        self.SetIcon(wx.Icon(cn.CN_ICON_CODE_VIEWER))
        self.SetSizer(sizer)
        if self.nav_frame.app_conf.vim_rect:
            self.SetRect(self.nav_frame.app_conf.vim_rect)
        else:
            self.CenterOnParent()

        self.entries = []
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_ESCAPE, cmd=wx.ID_CANCEL))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_F3, cmd=ID_FIND_NEXT))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_SHIFT, keyCode=wx.WXK_F3, cmd=ID_FIND_PREV))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_CTRL, keyCode=ord('F'), cmd=wx.ID_FIND))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_F4, cmd=ID_EDIT))
        self.SetAcceleratorTable(wx.AcceleratorTable(self.entries))

        self.Bind(wx.EVT_MENU, self.on_find, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.on_cancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_MENU, self.on_find_next, id=ID_FIND_NEXT)
        self.Bind(wx.EVT_MENU, self.on_find_prev, id=ID_FIND_PREV)
        self.Bind(wx.EVT_MENU, self.on_edit_ext, id=ID_EDIT)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def get_active_page(self):
        return None if self.page_ctrl.GetSelection() == -1 else self.page_ctrl.GetPage(self.page_ctrl.GetSelection())

    def on_edit_ext(self, e):
        page = self.get_active_page()
        if not page:
            print("cannot get active page")
            return
        selected = page.browser.get_file_name()
        if not selected:
            return
        if not self.nav_frame.app_conf.text_editor:
            self.nav_frame.show_message("External text editor is not defined")
            return
        args = [self.nav_frame.app_conf.text_editor]
        args.extend([selected])
        logger.debug(args)
        subprocess.Popen(args, shell=False)

    def close_page(self, index):
        page = self.page_ctrl.GetPage(index)
        page.browser.drop_file()
        self.page_ctrl.DeletePage(index)

    def close_all_pages(self):
        for index in range(self.page_ctrl.GetPageCount()):
            page = self.page_ctrl.GetPage(index)
            page.browser.drop_file()
        self.page_ctrl.DeleteAllPages()

    def on_find(self, e):
        page = self.get_active_page()
        if not page:
            return
        self.get_active_page().browser.search_pnl.Show()
        self.get_active_page().browser.search_pnl.ed_word.SetFocus()
        self.get_active_page().browser.search_pnl.ed_word.SelectAll()

    def on_find_next(self, e):
        if self.page_ctrl.GetPage(self.page_ctrl.GetSelection()).browser.search_pnl.ed_word.GetValue() == "":
            self.page_ctrl.GetPage(self.page_ctrl.GetSelection()).browser.search_pnl.ed_word.SetFocus()
        else:
            self.page_ctrl.GetPage(self.page_ctrl.GetSelection()).browser.search_pnl.on_search_forward(e)

    def on_find_prev(self, e):
        self.page_ctrl.GetPage(self.page_ctrl.GetSelection()).browser.search_pnl.on_search_backward(e)

    def on_cancel(self, e):
        self.Close()

    def set_caption(self):
        page = self.get_active_page()
        if page:
            self.SetTitle(f"{self.get_active_page().browser.get_file_name()} - {cn.CN_APP_NAME_VIEWER}"
                          if self.get_active_page().browser.get_file_name() else cn.CN_APP_NAME_VIEWER)
        else:
            self.SetTitle(cn.CN_APP_NAME_VIEWER)

    def on_close(self, e):
        self.Hide()
        wx.CallAfter(self.close_all_pages)

    def check_duplicates(self, file_name, high_opt):
        for index in range(self.page_ctrl.GetPageCount()):
            page = self.page_ctrl.GetPage(index)
            if page.file_name == file_name:
                self.page_ctrl.SetSelection(index)
                if high_opt.words:
                    browser = self.page_ctrl.GetPage(index).browser
                    browser.set_search_word(high_opt.words[0])
                    if high_opt.match == 1:
                        browser.reset_search()
                    browser.find_word(word=high_opt.words[0],
                                      case_sensitive=high_opt.case_sensitive,
                                      whole_word=high_opt.whole_words,
                                      only_mark=False,
                                      backward=False,
                                      match=high_opt.match)
                return index
        return -1

    def add_page(self, file_name, high_opt):
        if self.check_duplicates(file_name=file_name, high_opt=high_opt) >= 0:
            return True
        page = high_code.HtmlPanel(parent=self.page_ctrl, file_name=file_name)
        if not page.open_file(high_opt=high_opt):
            del page
            return False
        self.page_ctrl.AddPage(page=page, caption=Path(file_name).name, select=True)
        self.set_caption()
        return True

    def add_pages(self, file_names):
        result = False
        for file_name in file_names:
            if self.add_page(file_name=file_name, high_opt=high_code.HighOptions()):
                result = True
        return result

    def show_files(self, file_names):
        if self.add_pages(file_names=file_names):
            self.Show()
            if self.IsIconized():
                # self.RequestUserAttention()
                self.Restore()

    def show_file(self, file_name, high_opt):
        if self.add_page(file_name=file_name, high_opt=high_opt):
            self.Show()
            if self.IsIconized():
                # self.RequestUserAttention()
                self.Restore()









