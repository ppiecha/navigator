import wx
import wx.html2
from pygments.util import ClassNotFound
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
import constants as cn
import wx.aui as aui
from pathlib import Path


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
        page = HtmlPanel(parent=self.page_ctrl, frame=self, file_name=file_name)
        self.page_ctrl.AddPage(page=page, caption=Path(file_name).name, select=True)


class HtmlPanel(wx.Panel):
    def __init__(self, parent, frame, file_name):
        super().__init__(parent=parent)
        self.frame = frame
        self.source = ""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        self.set_page(file_name=file_name)
        sizer.Add(self.browser, flag=wx.EXPAND, proportion=1)
        self.browser.Find("class", wx.html2.WEBVIEW_FIND_HIGHLIGHT_RESULT)
        self.browser.SetFocus()
        self.SetSizer(sizer)

    def read_file(self, file_name):
        if not self.source:
            with open(file_name, "r") as f:
                return "".join(f.readlines())
        else:
            return self.source

    def set_page(self, file_name, formatter=HtmlFormatter(encoding='utf-8', style='emacs', linenos='table', full=True),
                 lexer=None):
        if not lexer:
            try:
                lexer = guess_lexer_for_filename(file_name, self.read_file(file_name))
            except ClassNotFound:
                lexer = get_lexer_by_name('text')

        self.browser.SetPage(highlight(self.read_file(file_name), lexer, formatter), "")

# class CodeFile:
#     def __init__(self, file_name):
#         with open(file_name, "r") as f:
#             self.source = "".join(f.readlines())
            # code = HTML("code", source)
            # pre = HTML("pre", str(code), escape=False)
            # body = HTML("body", str(pre), escape=False)
            # html = HTML("html", str(body), escape=False)
            # h = HTML("html")
            # self.html = str(HTML("pre", str(self.html.code("".join(file_lst)))))
            # b = h.body.pre.code("kuku")
            # print(b)
            # print(h)
            # self.html = html
            # self.html.code("".join(file_lst))
            # self.html./pre()

            # print(self.html)
