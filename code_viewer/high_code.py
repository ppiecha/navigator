import wx
import wx.html2
from pygments.util import ClassNotFound
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import controls
from util import constants as cn
from pathlib import Path
import os
from lib4py import logger as lg
import logging
logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)


class HtmlViewer(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.nav_frame = self.parent.parent.GetParent().nav_frame
        self.vw: wx.html2.WebView = wx.html2.WebView.New(self)
        self.vw.MSWSetEmulationLevel(wx.html2.WEBVIEWIE_EMU_IE11_FORCE)
        self.vw.SetZoomType(wx.html2.WEBVIEW_ZOOM_TYPE_TEXT)
        # self.vw.AcceleratorTable = self.parent.parent.GetAcceleratorTable()
        self.search_pnl = SearchPanel(parent=self, browser=self)
        self.search_pnl.Hide()
        self.files = {}
        self.word = ""
        self.word_cnt = -1

        self.drag_tgt = MyFileDropTarget(self.vw, self.on_process_dropped_files)
        self.vw.SetDropTarget(self.drag_tgt)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.search_pnl, flag=wx.EXPAND)
        sizer.Add(self.vw, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)
        # self.vw.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        # self.vw.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        # self.Bind(wx.EVT_CHILD_FOCUS, self.on_child_fous)


    def on_child_fous(self, e):
        logger.debug(f"ww key down {type(e)} {type(wx.Window.FindFocus())}")
        if isinstance(wx.Window.FindFocus(), wx.html2.WebView):
            logger.debug("HTML viewer")
        e.Skip()

        # if e.GetKeyCode() == wx.WXK_CONTROL_F:
        #     self.parent.parent.parent.on_find(e=None)

    def get_file_name(self):
        for file_name in self.files.keys():
            return file_name
        return ""

    def drop_file(self):
        if not self.get_file_name() in self.files.keys():
            raise ValueError("Wrong file name")
        else:
            del self.files[self.get_file_name()]

    def on_process_dropped_files(self, x, y, file_names):
        files = [f for f in file_names if Path(f).is_file()]
        if files:
            self.add_pages(file_names=files)
            return True
        else:
            return False
        # src_id = self.drag_src.win_id if self.drag_src else -1
        # tgt_id = self.drag_tgt.object.win_id
        # same_win = src_id == tgt_id
        # item, flags = self.HitTest((x, y))
        # if same_win:
        #     self.frame.move([f for f in file_names if Path(f).is_dir()],
        #                     [f for f in file_names if Path(f).is_file()],
        #                     self.path.joinpath(self.GetItemText(item)))
        #     return True
        # else:
        #     if src_id < 0:
        #         self.SetFocus()
        #     folders = [f for f in file_names if Path(f).exists() and Path(f).is_dir()]
        #     files = [f for f in file_names if Path(f).exists() and Path(f).is_file()]
        #     self.frame.copy(folders, files, str(self.path))
        #     return True

    def clear(self):
        self.vw.SetPage("", "")
        self.vw.Reload()

    def set_page(self, content, lexer, formatter):
        content = highlight(code=content,
                            lexer=lexer,
                            formatter=formatter)
        content = content.replace("<h2></h2>", "")
        #      content = content.replace("""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
        # "http://www.w3.org/TR/html4/strict.dtd">""", "")
        # content = content.replace("<body>", """<body style="font-family: Consolas">""")
        # <font face='verdana'>
        content = content.replace("body .hll { background-color: #ffffcc }",
                                  "body .hll { background-color: #282831 }")
        content = content.replace("body { background: #1e1e27; color: #cfbfad }", """body  { background: #1e1e27; color: #cfbfad;
        font-family: Consolas, monaco, monospace; font-size: 12px;}""")
        content = content.replace("td.linenos pre { color: #000000; background-color: #f0f0f0; padding-left: 5px; padding-right: 5px; }",
                                  """td.linenos pre { color: #7F7F7F; background-color: #1e1e27; padding-left: 5px; padding-right: 5px; }
                                  ::selection { color: black; background: yellow; }
                                  """)
        self.vw.SetPage(content, "")
        # self.vw.Reload()
        # self.vw.SetEditable(enable=True)

    def set_search_word(self, word):
        self.search_pnl.ed_word.SetValue(word)

    def read_file(self, file_name, reread=False):
        if file_name not in self.files.keys() or reread:
            try:
                with open(file_name, "r") as f:
                    self.files[file_name] = f.readlines()
                if not reread:
                    self.nav_frame.app_conf.hist_update_file(full_path=str(file_name),
                                                             callback=self.nav_frame.refresh_lists)
            except (UnicodeDecodeError, PermissionError, OSError) as e:
                self.nav_frame.show_message(f"Cannot open file {Path(file_name).absolute()} \n{str(e)}")
                return False
            else:
                return True
        else:
            return True

    def file_as_source(self, file_name, reread=False):
        if reread:
            if not self.read_file(file_name, reread=True):
                return ""
        if not self.read_file(file_name):
            return ""
        return "".join(self.files[file_name])

    def reload(self, reread=False):
        formatter = self.get_formatter(lines=[])
        self.set_page(content=self.file_as_source(self.get_file_name(), reread),
                      lexer=self.get_lexer(file_name=self.get_file_name()),
                      formatter=formatter)

    def show_file(self, file_name, high_opt, lexer=None, formatter=None):
        if not self.read_file(file_name):
            return False
        self.search_pnl.Show()
        if not high_opt:
            raise Exception("Highlight options not defined")
        if not lexer:
            lexer = self.get_lexer(file_name=file_name)
        if not formatter:
            formatter = self.get_formatter(lines=high_opt.lines)
        self.set_page(content=self.file_as_source(file_name),
                      lexer=lexer,
                      formatter=formatter)
        self.search_pnl.set_max_line(len(self.files[file_name]))
        if high_opt.words:
            self.set_search_word(high_opt.words[0])
            self.find_word(word=high_opt.words[0],
                           case_sensitive=high_opt.case_sensitive,
                           whole_word=high_opt.whole_words,
                           only_mark=False,
                           backward=False,
                           match=high_opt.match)
            self.go_to_left()
        return True

    def show_part(self, file_name, high_opt, line_delta, lexer=None, formatter=None):
        if not self.read_file(file_name):
            return False
        self.search_pnl.Hide()
        line = int(high_opt.lines[0] - 1)
        start = max([(line - line_delta), 0])
        stop = min([line + line_delta + 1, len(self.files[file_name])])
        content = "".join([" \n" if line == "\n" else line for line in self.files[file_name][start:stop]])
        if not lexer:
            lexer = self.get_lexer(file_name=file_name)
        if not formatter:
            formatter = self.get_formatter(lines=[1] if line == 0 else [2], linenostart=start+1)
        self.set_page(content=content,
                      lexer=lexer,
                      formatter=formatter)
        self.reset_search()
        self.find_word(word=high_opt.words[0],
                       case_sensitive=high_opt.case_sensitive,
                       whole_word=high_opt.whole_words,
                       only_mark=True,
                       backward=False,
                       match=-1)
        self.go_to_line(start+1)

    def reset_search(self):
        self.vw.Find("")
        self.word = ""

    def find_word(self, word, case_sensitive=False, whole_word=False, only_mark=False, backward=False, match=-1,
                  reset=False):
        flags = wx.html2.WEBVIEW_FIND_DEFAULT | wx.html2.WEBVIEW_FIND_WRAP | wx.html2.WEBVIEW_FIND_HIGHLIGHT_RESULT
        if case_sensitive:
            flags |= wx.html2.WEBVIEW_FIND_MATCH_CASE
        if whole_word:
            flags |= wx.html2.WEBVIEW_FIND_ENTIRE_WORD
        if backward:
            flags |= wx.html2.WEBVIEW_FIND_BACKWARDS
        if word != self.word or reset:
            self.word = word
            self.word_cnt = self.vw.Find(word, flags)
            if only_mark:
                return [-1, self.word_cnt]
        if match >= 0:
            match_num = self.vw.Find(word, flags)
            while match_num != match - 1:
                match_num = self.vw.Find(word, flags)
            self.search_pnl.update_count_label(word_num=match_num, word_cnt=self.word_cnt)
            return [match_num, self.word_cnt]
        else:
            match_num = self.vw.Find(word, flags)
            self.search_pnl.update_count_label(word_num=match_num, word_cnt=self.word_cnt)
            return [match_num, self.word_cnt]

    def get_lexer(self, file_name, lexer=""):
        if not lexer:
            try:
                lex = guess_lexer_for_filename(file_name, self.file_as_source(file_name))
                return lex
            except ClassNotFound:
                ext: str = Path(file_name).suffix
                if ext and ext.lower() in ('.pks', '.pkb'):
                    return get_lexer_by_name('sql')
                else:
                    return get_lexer_by_name('text')

    def get_formatter(self, style='inkpot', linenos='table', lines=[], linenostart=1):
        return HtmlFormatter(#encoding='utf-8',
                             style=style,
                             linenos=linenos,
                             full=True,
                             # lineanchors='ln',
                             linespans='line',
                             # anchorlinenos=True,
                             hl_lines=lines,
                             linenostart=linenostart)

    def go_to_line(self, line_no=None):
        self.vw.RunScript('document.getElementById("line-' + str(line_no) + '").scrollIntoView(true);')
        self.go_to_left()

    def go_to_left(self):
        self.vw.RunScript('window.scrollTo(0, window.pageYOffset);')
        # self.vw.RunScript('window.scrollTo(0, 0);')


class SearchPanel(wx.Panel):
    def __init__(self, parent, browser):
        super().__init__(parent=parent)
        self.browser = browser
        self.ed_line = wx.SpinCtrl(parent=self, min=1, initial=1)
        self.lbl_all_lines = wx.StaticText(parent=self)
        self.ed_lexer = wx.ComboBox(self, style=wx.CB_READONLY | wx.CB_SORT)
        self.ed_word = wx.SearchCtrl(parent=self)
        self.ed_word.ShowCancelButton(True)
        self.btn_prev = controls.ToolBtn(self, cn.CN_IM_SEARCH_UP, def_ctrl=[browser])
        self.btn_prev.SetToolTip(wx.ToolTip("Find previous (Shift+F3)"))
        self.btn_next = controls.ToolBtn(self, cn.CN_IM_SEARCH_DOWN, def_ctrl=[browser])
        self.btn_next.SetToolTip(wx.ToolTip("Find next (F3)"))
        self.lbl_cnt = wx.StaticText(parent=self)
        self.btn_case = controls.ToggleBtn(self, cn.CN_IM_CASE_OFF, cn.CN_IM_CASE, def_ctrl=[browser])
        self.btn_whole = controls.ToggleBtn(self, cn.CN_IM_WORD_OFF, cn.CN_IM_WORD, def_ctrl=[browser])
        # self.btn_close = controls.ToolBtn(self, cn.CN_IM_CLOSE, def_ctrl=[browser])

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(wx.StaticText(parent=self, label="Line"), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.sizer.Add(self.ed_line, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.sizer.Add(self.lbl_all_lines, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.sizer.Add(self.ed_lexer, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=5)
        self.sizer.Add(wx.Panel(self), flag=wx.EXPAND, proportion=1)
        self.sizer.Add(self.lbl_cnt, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.sizer.AddMany([self.ed_word, self.btn_prev, self.btn_next, self.btn_case, self.btn_whole])
        self.SetSizer(self.sizer)

        self.ed_word.Bind(wx.EVT_TEXT, self.on_search_forward)

        self.btn_next.Bind(wx.EVT_BUTTON, self.on_search_forward)
        self.btn_prev.Bind(wx.EVT_BUTTON, self.on_search_backward)
        self.ed_line.Bind(wx.EVT_TEXT, self.go_to_line)
        self.btn_case.Bind(wx.EVT_TOGGLEBUTTON, self.on_reset_search)
        self.btn_whole.Bind(wx.EVT_TOGGLEBUTTON, self.on_reset_search)
        self.ed_lexer.Bind(wx.EVT_COMBOBOX, self.on_select_lexer)

        self.load_lexers()

    def load_lexers(self):
        name_tuples = [b for a, b, *c in get_all_lexers()]
        self.ed_lexer.SetItems([name[0] for name in name_tuples if len(name) >= 1])
        # print(name_tuples)
        # self.ed_lexer.SetItems([item[0] for item in name_tuples])
        # for item in get_all_lexers():
        #     print(item[1])

    def on_select_lexer(self, e):
        formatter = self.browser.get_formatter(lines=[])
        self.browser.set_page(content=self.browser.file_as_source(self.browser.get_file_name()),
                              lexer=get_lexer_by_name(self.ed_lexer.GetStringSelection()),
                              formatter=formatter)

    def set_max_line(self, max_line):
        self.lbl_all_lines.SetLabel(f"/{max_line}")
        self.ed_line.SetMax(max_line)

    def go_to_line(self, e):
        if self.ed_line.GetValue() <= self.ed_line.GetMax():
            self.browser.go_to_line(self.ed_line.GetValue())

    def resize(self):
        self.sizer.Layout()

    def on_reset_search(self, e):
        self.do_search(word=self.ed_word.GetValue(),
                       case_sensitive=self.btn_case.GetValue(),
                       whole_word=self.btn_whole.GetValue(),
                       backward=False,
                       reset=True)

    def on_search_forward(self, e):
        self.do_search(word=self.ed_word.GetValue(),
                       case_sensitive=self.btn_case.GetValue(),
                       whole_word=self.btn_whole.GetValue(),
                       backward=False)

    def on_search_backward(self, e):
        self.do_search(word=self.ed_word.GetValue(),
                       case_sensitive=self.btn_case.GetValue(),
                       whole_word=self.btn_whole.GetValue(),
                       backward=True)

    def do_search(self, word, case_sensitive, whole_word, backward=False, reset=False):
        word_num, word_cnt = self.browser.find_word(word=word,
                                                    case_sensitive=case_sensitive, # button pressed
                                                    whole_word=whole_word, # button pressed
                                                    only_mark=False,
                                                    backward=backward,
                                                    reset=reset)
        # self.update_count_label(word_num=word_num, word_cnt=word_cnt)

    def update_count_label(self, word_num: int, word_cnt: int):
        if word_num >= 0:
            self.lbl_cnt.SetLabel(f"{str(word_num + 1)}/{str(word_cnt)}")
        else:
            self.lbl_cnt.SetLabel("")
        self.resize()


class HtmlPanel(wx.Panel):
    def __init__(self, parent, file_name):
        super().__init__(parent=parent)
        self.parent = parent
        self.browser = HtmlViewer(parent=self)
        self.file_name = file_name
        self.deleted: bool = False
        if file_name:
            self.stat = os.stat(file_name, follow_symlinks=False).st_mtime

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.browser, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)

    def to_be_reloaded(self, file_name):
        if not self.deleted:
            if not Path(file_name).exists():
                self.deleted = True
                dlg = wx.MessageDialog(self, f"File {file_name} doesn't exist. Keep in code viewer?",
                                       style=wx.YES_NO | wx.ICON_INFORMATION,
                                       caption=cn.CN_APP_NAME)
                resp = dlg.ShowModal()
                if resp == wx.ID_YES:
                    return wx.ID_CANCEL
                else:
                    logger.debug(f"deleting page {self.parent.GetSelection()}")
                    wx.CallAfter(self.parent.viewer_frame.close_page, self.parent.GetSelection())
                    return wx.ID_CANCEL
            else:
                # logger.debug(f"{file_name} exists")
                stat = os.stat(file_name, follow_symlinks=False).st_mtime
                if self.stat != stat:
                    dlg = wx.MessageDialog(self, f"File {file_name} has changed. Reload?",
                                           style=wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION,
                                           caption=cn.CN_APP_NAME)
                    self.stat = stat
                    return dlg.ShowModal()
                else:
                    return wx.ID_CANCEL

    def open_file(self, high_opt):
        return self.browser.show_file(file_name=self.file_name, high_opt=high_opt)


class HighOptions:
    def __init__(self, words=[], case_sensitive=False, whole_words=False, match=-1, lines=[]):
        self.words = words
        self.case_sensitive = case_sensitive
        self.whole_words = whole_words
        self.match = match
        self.lines = lines


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, object, target_processor):
        super().__init__()
        self.object = object
        self.target_processor = target_processor

    def OnDropFiles(self, x, y, filenames):
        return self.target_processor(x, y, filenames)

    # def OnDragOver(self, x, y, defResult):
    #     src_id = self.object.drag_src.win_id if self.object.drag_src else -1
    #     tgt_id = self.object.drag_tgt.object.win_id
    #     item, flags = self.object.HitTest((x, y))
    #     if src_id == tgt_id:
    #         if item < 0:
    #             return wx.DragNone
    #         else:
    #             path = self.object.path.joinpath(self.object.GetItemText(item))
    #             return wx.DragCopy if path.is_dir() else wx.DragNone
    #     else:
    #         return wx.DragCopy