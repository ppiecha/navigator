import wx
import wx.html2
import constants as cn
import wx.aui as aui
from pathlib import Path
from code_viewer import high_code

ID_FIND_NEXT = wx.NewId()
ID_FIND_PREV = wx.NewId()

class MainFrame(wx.Frame):
    def __init__(self, nav_frame):
        super().__init__(parent=nav_frame, title=cn.CN_APP_NAME_VIEWER, size=(800, 600), style=wx.DEFAULT_FRAME_STYLE)
        self.page_ctrl = aui.AuiNotebook(parent=self, style=aui.AUI_NB_CLOSE_ON_ALL_TABS | aui.AUI_NB_SCROLL_BUTTONS |
                                                            aui.AUI_NB_TOP)
        self.nav_frame = nav_frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.page_ctrl, flag=wx.EXPAND, proportion=1)
        self.SetIcon(wx.Icon(cn.CN_ICON_CODE_VIEWER))
        self.SetSizer(sizer)
        self.CenterOnScreen()

        self.entries = []
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_ESCAPE, cmd=wx.ID_CANCEL))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_F3, cmd=ID_FIND_NEXT))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_SHIFT, keyCode=wx.WXK_F3, cmd=ID_FIND_PREV))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_CTRL, keyCode=ord('F'), cmd=wx.ID_FIND))
        self.SetAcceleratorTable(wx.AcceleratorTable(self.entries))

        self.Bind(wx.EVT_MENU, self.on_find, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.on_cancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_MENU, self.on_find_next, id=ID_FIND_NEXT)
        self.Bind(wx.EVT_MENU, self.on_find_prev, id=ID_FIND_PREV)
        self.page_ctrl.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.page_changed)
        self.page_ctrl.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.page_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def page_close(self, e):
        pt = wx.GetMousePosition()
        tab_index, flag = self.page_ctrl.HitTest(self.ScreenToClient(pt))
        page = self.page_ctrl.GetPage(tab_index)
        page.browser.drop_file()
        e.Skip()

    def get_active_page(self):
        # print(self.page_ctrl.GetSelection())
        return self.page_ctrl.GetPage(self.page_ctrl.GetSelection())

    def on_find(self, e):
        self.get_active_page().browser.search_pnl.Show()
        self.get_active_page().browser.search_pnl.ed_word.SetFocus()

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
        self.SetTitle(f"{self.get_active_page().browser.get_file_name()} - {cn.CN_APP_NAME_VIEWER}"
                      if self.get_active_page().browser.get_file_name() else cn.CN_APP_NAME_VIEWER)

    def page_changed(self, e):
        self.set_caption()
        e.Skip()

    def on_close(self, e):
        self.Hide()

    def check_duplicates(self, file_name, high_opt):
        for index in range(self.page_ctrl.GetPageCount()):
            if self.page_ctrl.GetPage(index).file_name == file_name:
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









