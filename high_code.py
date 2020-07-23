import wx
import wx.html2
from pygments.util import ClassNotFound
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
import controls
import constants as cn


class HtmlViewer(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.vw = wx.html2.WebView.New(self)
        self.search = SearchPanel(parent=self, browser=self)
        self.files = {}
        self.word = ""
        self.word_cnt = -1

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.search, flag=wx.EXPAND)
        sizer.Add(self.vw, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)

    def read_file(self, file_name):
        if file_name not in self.files.keys():
            with open(file_name, "r") as f:
                self.files[file_name] = f.readlines()
        return self.files[file_name]

    def file_as_source(self, file_name):
        self.read_file(file_name)
        return "".join(self.files[file_name])

    def show_file(self, file_name, lines=[], lexer=None, formatter=None):
        if not lexer:
            lexer = self.get_lexer(file_name=file_name)
        if not formatter:
            formatter = self.get_formatter(lines=lines)
        self.read_file(file_name)
        self.vw.SetPage(highlight(code=self.file_as_source(file_name),
                                  lexer=lexer,
                                  formatter=formatter),
                        "")

    def show_part(self, file_name, line, line_delta, word=None, lexer=None, formatter=None):
        pass

    def find_word(self, word, case_sensitive=False, whole_word=False, high_all=True, backward=False):
        flags = wx.html2.WEBVIEW_FIND_DEFAULT | wx.html2.WEBVIEW_FIND_WRAP
        if case_sensitive:
            flags |= wx.html2.WEBVIEW_FIND_MATCH_CASE
        if whole_word:
            flags |= wx.html2.WEBVIEW_FIND_ENTIRE_WORD
        if high_all:
            flags |= wx.html2.WEBVIEW_FIND_HIGHLIGHT_RESULT
        if backward:
            flags |= wx.html2.WEBVIEW_FIND_BACKWARDS
        if word != self.word:
            self.word = word
            self.word_cnt = self.vw.Find(word, flags)
        return [self.vw.Find(word, flags), self.word_cnt]

    def get_lexer(self, file_name, lexer=""):
        if not lexer:
            try:
                return guess_lexer_for_filename(file_name, self.file_as_source(file_name))
            except ClassNotFound:
                return get_lexer_by_name('text')

    def get_formatter(self, style='emacs', linenos='table', lines=[], linenostart=1):
        return HtmlFormatter(encoding='utf-8',
                             style=style,
                             linenos=linenos,
                             full=True,
                             # lineanchors='ln',
                             linespans='line',
                             # anchorlinenos=True,
                             hl_lines=lines,
                             linenostart=linenostart)

    def go_to_line(self, line_no=None):
        # print('document.getElementById("line-' + str(line_no) + '").scrollIntoView(true);')
        # self.vw.RunScript(f"window.location.hash = 'line-{str(line_no)}';")
        self.vw.RunScript('document.getElementById("line-' + str(line_no) + '").scrollIntoView(true);')
        self.vw.RunScript('window.scrollTo(0, window.pageYOffset);')


class SearchPanel(wx.Panel):
    def __init__(self, parent, browser):
        super().__init__(parent=parent)
        self.browser = browser

        self.ed_word = wx.SearchCtrl(parent=self)
        self.ed_word.ShowCancelButton(True)
        self.btn_prev = controls.ToolBtn(self, cn.CN_IM_SEARCH_UP, def_ctrl=[browser])
        self.btn_next = controls.ToolBtn(self, cn.CN_IM_SEARCH_DOWN, def_ctrl=[browser])
        self.lbl_cnt = wx.StaticText(parent=self)
        self.btn_case = controls.ToggleBtn(self, cn.CN_IM_FILTER_OFF, cn.CN_IM_FILTER, def_ctrl=[browser])
        self.btn_whole = controls.ToggleBtn(self, cn.CN_IM_FILTER_OFF, cn.CN_IM_FILTER, def_ctrl=[browser])
        self.btn_close = controls.ToolBtn(self, cn.CN_IM_CLOSE, def_ctrl=[browser])

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(wx.Panel(self), flag=wx.EXPAND, proportion=1)
        self.sizer.Add(self.lbl_cnt, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.sizer.AddMany([self.ed_word, self.btn_prev, self.btn_next, self.btn_case, self.btn_whole,
                            self.btn_close])
        self.SetSizer(self.sizer)

        self.ed_word.Bind(wx.EVT_TEXT, self.on_search_forward)

        self.btn_next.Bind(wx.EVT_BUTTON, self.on_search_forward)
        self.btn_prev.Bind(wx.EVT_BUTTON, self.on_search_backward)

    def resize(self):
        self.sizer.Layout()

    def on_search_forward(self, e):
        self.do_search()

    def on_search_backward(self, e):
        self.do_search(backward=True)

    def do_search(self, backward=False):
        word_num, word_cnt = self.browser.find_word(word=self.ed_word.GetValue(),
                                                    case_sensitive=False, # button pressed
                                                    whole_word=False, # button pressed
                                                    high_all=True,
                                                    backward=backward)
        if word_num >= 0:
            self.lbl_cnt.SetLabel(f"{str(word_num + 1)}/{str(word_cnt)}")
        else:
            self.lbl_cnt.SetLabel("")
        self.resize()


class HtmlPanel(wx.Panel):
    def __init__(self, parent, file_name):
        super().__init__(parent=parent)

        self.browser = HtmlViewer(parent=self)
        self.browser.show_file(file_name=file_name)
        # print(self.browser.vw.Find("function", wx.html2.WEBVIEW_FIND_HIGHLIGHT_RESULT))
        # self.browser.go_to_line(66)
        self.browser.SetFocus()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.browser, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)
