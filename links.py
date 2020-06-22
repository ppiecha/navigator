import wx
import dialogs
import wx.aui as aui
import wx.dataview as dv
# import wx.dataview.TreeListCtrl as tlc

class LinkPages:
    def __init__(self):
        self.pages = {"Links": []}


class SimpleLinkItem:
    """
    Dir
    File
    Hyper Link
    Command
    """
    """
    Name Description Target
    """
    def __init__(self, name, desc, target, params=[], children=[]):
        self.name = name
        self.desc = desc
        self.target = target
        self.params = params
        self.children = children


class LinkDlg(dialogs.BasicDlg):
    def __init__(self, frame, link_pages=None, edit=False):
        super().__init__(frame, "Links", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                         border=10 if edit else 0)
        if not edit:
            self.dlg_sizer.ShowItems(False)
            self.static_line.Show(False)
        self.link_pages = link_pages if link_pages else LinkPages()
        self.page_ctrl = LinkPageCtrl(self, frame)
        self.page_ctrl.load_pages(self.link_pages.pages)
        self.ctrl_sizer.Add(self.page_ctrl, flag=wx.EXPAND, proportion=1)


class LinkPageCtrl(aui.AuiNotebook):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, style=aui.AUI_NB_TAB_MOVE |  # aui.AUI_NB_TAB_SPLIT |
                                              aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_BOTTOM)
        self.SetArtProvider(aui.AuiDefaultTabArt())
        self.frame = frame

    def load_pages(self, pages):
        for page in pages.keys():
            self.add_page(page, pages[page])

    def add_page(self, name, items):
        page = LinkPanel(self, self.frame, items)
        self.AddPage(page=page, caption=name)


class LinkPanel(wx.Panel):
    def __init__(self, parent, frame, items=[]):
        super().__init__(parent=parent)
        self.frame = frame
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.link_items = TreeCtrl(self, frame)
        self.main_sizer.Add(self.link_items, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(self.main_sizer)


class TreeCtrl(dv.TreeListCtrl):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, style=dv.TL_DEFAULT_STYLE | dv.TL_NO_HEADER, size=(400, 300))
        #, style=0, size=(500, 300), agwStyle=tlc.TR_DEFAULT_STYLE |
                                                 # tlc.TR_HAS_BUTTONS |
                                                 # tlc.TR_TWIST_BUTTONS |
                                                 # tlc.TR_ROW_LINES |
                                                 # tlc.TR_COLUMN_LINES |
                                                 # tlc.TR_NO_LINES |
                                                 # tlc.TR_LINES_AT_ROOT |
                                                 # tlc.TR_FULL_ROW_HIGHLIGHT |
                                                 # tlc.TR_AUTO_TOGGLE_CHILD |
                                                 # tlc.TR_ELLIPSIZE_LONG_ITEMS |
                                                 # tlc.TR_NO_HEADER
                        # )
        self.frame = frame
        self.AppendColumn("Name")
        self.AppendColumn("Description")
        self.AppendColumn("Target")
        ch1 = self.AppendItem(self.GetRootItem(), "Name1")
        self.SetItemText(ch1, 1, "column1")
        self.SetItemText(ch1, 2, "column2")
        ch2 = self.AppendItem(self.GetRootItem(), "desc1")
        child1 = self.AppendItem(ch1, "child1")
        child2 = self.AppendItem(ch2, "child2")



