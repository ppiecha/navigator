import wx
import wx.html2
from pygments.util import ClassNotFound
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles


class HtmlViewer(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.vw = wx.html2.WebView.New(self)
        self.files = {}
        self.found_cnt = -1

        sizer = wx.BoxSizer(wx.VERTICAL)
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

    def show_file(self, file_name, lines=None, lexer=None, formatter=None):
        if not lexer:
            lexer = self.get_lexer(file_name=file_name)
        if not formatter:
            formatter = self.get_formatter(lines=lines)
        self.read_file(file_name)
        self.vw.SetPage(highlight(code=self.file_as_source(file_name),
                                  lexer=lexer,
                                  formatter=formatter),
                        "")

    def show_part(self, file_name, line_from, line_to, line, word=None, lexer=None, formatter=None):
        pass

    def find_word(self, word, case_sensitive=False, whole_word=False, high_all=False, backward=False):
        flags = wx.html2.WEBVIEW_FIND_DEFAULT | wx.html2.WEBVIEW_FIND_WRAP
        if case_sensitive:
            flags |= wx.html2.WEBVIEW_FIND_MATCH_CASE
        if whole_word:
            flags |= wx.html2.WEBVIEW_FIND_ENTIRE_WORD
        if high_all:
            flags |= wx.html2.WEBVIEW_FIND_HIGHLIGHT_RESULT
        if backward:
            flags |= wx.html2.WEBVIEW_FIND_BACKWARDS
        self.vw.Find(word, flags)
        return []

    def get_lexer(self, file_name, lexer=""):
        if not lexer:
            try:
                return guess_lexer_for_filename(file_name, self.file_as_source(file_name))
            except ClassNotFound:
                return get_lexer_by_name('text')

    def get_formatter(self, style='emacs', linenos='table', lines=[]):
        return HtmlFormatter(encoding='utf-8',
                             style=style,
                             linenos=linenos,
                             full=True,
                             # lineanchors='ln',
                             linespans='line',
                             # anchorlinenos=True,
                             hl_lines=lines)

    def go_to_line(self, line_no=None):
        # print('document.getElementById("line-' + str(line_no) + '").scrollIntoView(true);')
        # self.vw.RunScript(f"window.location.hash = 'line-{str(line_no)}';")
        self.vw.RunScript('document.getElementById("line-' + str(line_no) + '").scrollIntoView(true);')
        self.vw.RunScript('window.scrollTo(0, window.pageYOffset);')


class HtmlPanel(wx.Panel):
    def __init__(self, parent, file_name):
        super().__init__(parent=parent)

        self.browser = HtmlViewer(parent=self)
        # self.set_page(file_name=file_name)
        self.browser.show_file(file_name=file_name, lines=[11, 14, 17])
        print(self.browser.vw.Find("function", wx.html2.WEBVIEW_FIND_HIGHLIGHT_RESULT))
        self.browser.go_to_line(66)
        self.browser.SetFocus()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.browser, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)
