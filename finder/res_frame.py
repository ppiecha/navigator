from pathlib import Path
import wx
import search_tree
import search_const as cn
import search


class MainFrame(wx.MiniFrame):
    def __init__(self, finder, search_params):
        super().__init__(parent=None, title="Search results", size=(600, 600), style=wx.DEFAULT_FRAME_STYLE)
        self.SetDoubleBuffered(True)
        self.finder = finder
        self.status_bar = self.CreateStatusBar(1)
        self.search_params = search_params
        self.searches = []
        self.output = MainPanel(self, self)

        self.Center()

        self.Bind(wx.EVT_CLOSE, self.on_close)

        wx.CallAfter(self.start_search, self.search_params)

    def start_search(self, opt):
        s = search.Search(self, opt)
        self.searches.append(s)
        s.start()

    def on_close(self, e):
        self.finder.Close()
        e.Skip()


class MainPanel(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.frame = frame
        self.tree = search_tree.SearchTree(parent=self, main_frame=frame)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(sizer)