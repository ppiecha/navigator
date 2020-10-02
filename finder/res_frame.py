import threading
import wx
import wx.lib.buttons as buttons
import search
import search_const as cn
import search_tree
from code_viewer import high_code
import logging
from lib4py import logger as lg

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)

CN_ID_FIND = wx.NewId()


class MainFrame(wx.Frame):
    def __init__(self, finder):
        super().__init__(parent=None, title=cn.CN_APP_RESULTS, size=(395, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.SetDoubleBuffered(True)
        self.SetIcon(wx.Icon(cn.CN_ICON_FILE_NAME))
        self.finder = finder
        self.nav_frame = finder.nav_frame
        self.status_bar = self.CreateStatusBar(number=1, style=wx.STB_ELLIPSIZE_MIDDLE)
        self.search_params = None
        self.search_thread = None
        self.output = MainPanel(res_frame=self)

        self.CenterOnScreen()

        self.entries = []
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_ESCAPE, cmd=wx.ID_CANCEL))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_F3, cmd=CN_ID_FIND))
        # self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_CTRL, keyCode=ord("U"), cmd=CN_ID_UPPER))

        self.SetAcceleratorTable(wx.AcceleratorTable(self.entries))

        self.Bind(wx.EVT_MENU, self.on_cancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_MENU, self.on_find, id=CN_ID_FIND)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_find(self, e):
        data = self.output.tree.GetSelection().GetData()
        if isinstance(data, search_tree.FileNode):
            lines = [line.line_num for line in data.lines]
            high_opt = high_code.HighOptions(words=self.search_params.words,
                                             case_sensitive=self.search_params.case_sensitive,
                                             whole_words=self.search_params.whole_words,
                                             match=1,
                                             lines=lines)
            # self.finder.nav_frame.vim.get_active_page().browser.reset_search()
            self.finder.nav_frame.vim.show_file(file_name=data.file_full_name, high_opt=high_opt)

    def on_cancel(self, e):
        self.Close()

    def change_icon(self, event):
        if event.is_set():
            self.output.tool_pnl.btn_params.set_bitmap(cn.CN_IM_SEARCH)
        else:
            self.output.tool_pnl.btn_params.set_bitmap(cn.CN_IM_STOP)

    def start_search(self):
        logger.debug(f"Search params {self.search_params}")
        self.start_search_thread(self.search_params)

    def set_params(self, search_params):
        self.search_params = search_params

    def start_search_thread(self, opt):
        del self.search_thread
        self.search_thread = search.Search(self, opt, threading.Event())
        self.change_icon(self.search_thread.event)
        self.output.tree.init_tree()
        self.search_thread.start()

    def cancel_search_thread(self):
        self.search_thread.event.set()
        if self.search_thread.is_alive():
            self.search_thread.join()
        self.change_icon(self.search_thread.event)

    def on_close(self, e):
        self.cancel_search_thread()
        self.Hide()

        # self.finder.Destroy()
        # self.Destroy()


class MainPanel(wx.Panel):
    def __init__(self, res_frame):
        super().__init__(parent=res_frame)
        self.res_frame = res_frame
        self.tree = search_tree.SearchTree(parent=self, res_frame=res_frame)
        self.tool_pnl = ToolPanel(parent=self, res_frame=res_frame)
        self.preview = high_code.HtmlPanel(parent=self, file_name="")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tool_pnl)
        sizer.Add(self.tree, flag=wx.EXPAND, proportion=1)
        sizer.Add(self.preview, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)


class ToolPanel(wx.Panel):
    def __init__(self, parent, res_frame):
        super().__init__(parent=parent)
        self.res_frame = res_frame
        self.main_pnl = parent
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_params = ToolBtn(self, im_file=cn.CN_IM_SEARCH, def_ctrl=[parent.tree])
        self.btn_expand_all = ToolBtn(self, im_file=cn.CN_IM_EXPAND, def_ctrl=[parent.tree])
        self.btn_collapse_all = ToolBtn(self, im_file=cn.CN_IM_COLLAPSE, def_ctrl=[parent.tree])

        sizer.Add(self.btn_params)
        sizer.Add(self.btn_expand_all)
        sizer.Add(self.btn_collapse_all)

        self.SetSizer(sizer)

        self.btn_params.Bind(wx.EVT_BUTTON, self.on_params)
        self.btn_expand_all.Bind(wx.EVT_BUTTON, self.on_expand_all)
        self.btn_collapse_all.Bind(wx.EVT_BUTTON, self.on_collapse_all)

    def on_params(self, e):
        if not self.res_frame.search_thread.event.is_set():
            self.res_frame.cancel_search_thread()
        else:
            self.res_frame.finder.Show()

    def on_expand_all(self, e):
        self.main_pnl.tree.ExpandAll()

    def on_collapse_all(self, e):
        self.main_pnl.tree.collapse_all()


class ToolBtn(buttons.ThemedGenBitmapButton):
    def __init__(self, parent, im_file, def_ctrl=[], size=(24, 24)):
        super().__init__(parent, -1, wx.Bitmap(im_file, wx.BITMAP_TYPE_PNG), size=size)
        self.def_ctrl = def_ctrl
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)

    def AcceptsFocusFromKeyboard(self):
        return False

    def on_focus(self, event):
        if self.def_ctrl:
            self.def_ctrl[0].SetFocus()
            return
        event.Skip()

    def set_bitmap(self, im_file):
        self.SetBitmapLabel(wx.Bitmap(im_file, wx.BITMAP_TYPE_PNG))
        self.Refresh()

    def set_off_bitmap(self, im_file):
        self.SetBitmapDisabled(wx.Bitmap(im_file, wx.BITMAP_TYPE_PNG))
