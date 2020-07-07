from pathlib import Path
import wx
import search_tree
import search_const as cn
import search
import wx.lib.buttons as buttons
import threading


class MainFrame(wx.Frame):
    def __init__(self, finder):
        super().__init__(parent=None, title=cn.CN_APP_RESULTS, size=(395, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.SetDoubleBuffered(True)
        self.SetIcon(wx.Icon(cn.CN_ICON_FILE_NAME))
        self.finder = finder
        self.status_bar = self.CreateStatusBar(1)
        self.search_params = None
        self.search_thread = None
        self.output = MainPanel(frame=self)

        self.Center()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def change_icon(self, event):
        if event.is_set():
            self.output.tool_pnl.btn_params.set_bitmap(cn.CN_IM_NEW_SEARCH)
        else:
            self.output.tool_pnl.btn_params.set_bitmap(cn.CN_IM_STOP)

    def start_search(self):
        print(self.search_params)
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
        print("event set")
        if self.search_thread.is_alive():
            print("alive before join")
            self.search_thread.join()
        print("event stopped")
        self.change_icon(self.search_thread.event)

    def on_close(self, e):
        self.finder.Destroy()
        self.Destroy()


class MainPanel(wx.Panel):
    def __init__(self, frame):
        super().__init__(parent=frame)
        self.frame = frame
        self.tree = search_tree.SearchTree(parent=self, frame=frame)
        self.tool_pnl = ToolPanel(parent=self, frame=frame)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tool_pnl)
        sizer.Add(self.tree, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(sizer)


class ToolPanel(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.frame = frame
        self.main_pnl = parent
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_params = ToolBtn(self, im_file=cn.CN_IM_NEW_SEARCH, def_ctrl=[parent.tree])
        self.btn_expand_all = ToolBtn(self, im_file=cn.CN_IM_NEW_SEARCH, def_ctrl=[parent.tree])
        self.btn_collapse_all = ToolBtn(self, im_file=cn.CN_IM_NEW_SEARCH, def_ctrl=[parent.tree])

        sizer.Add(self.btn_params)
        sizer.Add(self.btn_expand_all)
        sizer.Add(self.btn_collapse_all)

        self.SetSizer(sizer)

        self.btn_params.Bind(wx.EVT_BUTTON, self.on_params)
        self.btn_expand_all.Bind(wx.EVT_BUTTON, self.on_expand_all)
        self.btn_collapse_all.Bind(wx.EVT_BUTTON, self.on_collapse_all)

    def on_params(self, e):
        if not self.frame.search_thread.event.is_set():
            self.frame.cancel_search_thread()
        else:
            self.frame.finder.Show()

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
