from pathlib import Path
import wx
import search_tree
import search_const as cn
import search


class MainFrame(wx.MiniFrame):
    def __init__(self, finder, search_params):
        super().__init__(parent=None, title="Search results", size=(395, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.finder = finder
        self.status_bar = self.CreateStatusBar(1)
        self.search_params = search_params
        self.searches = []
        self.output = MainPanel(self, self)
        print(search_params.words)

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
        root = self.tree.add_root_node("Search results")
        # file = self.tree.add_file_node("file name 0 matches")
        # self.tree.add_line_node(file, str(1), "self.SetSize(self.GetEffectiveMinSize())", "word")
        # self.tree.add_line_node(file, str(23), "very complicated text", "word")
        # self.tree.add_line_node(file, str(234), "wx.CallAfter(self.start_search, self.search_params)", "word")
        # file2 = self.tree.add_file_node("bacl_lab.py 3 matches")
        # self.tree.add_line_node(file2, str(1), "CN_IM_FOLDER = os.path.join(CN_APP_PATH", "word")
        # self.tree.add_line_node(file2, str(2354), "very complicated text", "word")
        # self.tree.add_line_node(file2, str(23465), "CN_IM_FOLDER = os.path.join(CN_APP_PATH", "word")
        self.tree.Expand(root)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tree, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(sizer)