import wx
import wx.html2
import constants as cn
import wx.aui as aui
from pathlib import Path
import high_code


class MainFrame(wx.Frame):
    def __init__(self, frame, file_name):
        super().__init__(parent=frame, title=cn.CN_APP_NAME_VIEWER, size=(800, 600), style=wx.DEFAULT_FRAME_STYLE)
        self.page_ctrl = aui.AuiNotebook(parent=self, style=aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS |
                                                            aui.AUI_NB_TOP)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.page_ctrl, flag=wx.EXPAND, proportion=1)
        self.add_page(file_name=file_name)
        # self.SetIcon(wx.Icon(cn.CN_ICON_FILE_NAME))
        self.SetSizer(sizer)
        self.CenterOnScreen()

        self.page_ctrl.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.page_changed)

    def page_changed(self, e):
        e.GetPage().browser.SetFocus()
        print("page")
        e.Skip()

    def add_page(self, file_name):
        page = high_code.HtmlPanel(parent=self.page_ctrl, file_name=file_name)
        self.page_ctrl.AddPage(page=page, caption=Path(file_name).name, select=True)





