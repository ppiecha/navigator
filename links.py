import wx
import dialogs
import constants as cn


class LinkPages:
    def __init__(self, pages=[]):
        self.pages = pages if pages else [LinkPage(page_name="Default",
                                                   page_items=[LinkItem(name="item1", desc="desc1", target="C:\\temp"),
                                                               LinkItem(name="item2", desc="desc2", target="C:\\temp2")
                                                               ]),
                                          LinkPage(page_name="Next one",
                                                   page_items=[LinkItem(name="item3", desc="desc3", target="C:\\temp"),
                                                               LinkItem(name="item4", desc="desc4", target="C:\\temp2")
                                                               ])
                                         ]


class LinkPage:
    def __init__(self, page_name=None, page_items=[], children=[]):
        self.page_name = page_name
        self.page_items = page_items
        self.children = children

class LinkItem:
    """
    Dir
    File
    Hyper Link
    Command
    """
    """
    Name Description Target
    """
    def __init__(self, name, type=0, desc="", target="", params=[]):
        self.name = name
        """
        0 - folder
        1 - file
        3 - shortcut
        4 - hiperlink
        """
        self.type = type
        self.desc = desc
        self.target = target
        self.params = params


class SimpleMiniFrame(wx.MiniFrame):
    def __init__(self, frame, is_left, is_read_only):
        super().__init__(parent=frame, title=cn.CN_TOOL_NAME + " (left)" if is_left else cn.CN_TOOL_NAME + " (right)",
                         style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX)
        self.frame = frame
        self.is_left = is_left
        self.is_read_only = is_read_only

        self.SetAcceleratorTable(wx.AcceleratorTable([wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL,
                                                                          keyCode=wx.WXK_ESCAPE,
                                                                          cmd=wx.ID_CANCEL)]))

        # sizers
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mid_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Dialog buttons
        self.static_line = wx.StaticLine(self)
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label="OK")
        self.btn_ok.SetDefault()
        self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="Cancel")

        # Add buttons
        self.sep = wx.Panel(self)
        self.btn_sizer.Add(self.sep, flag=wx.EXPAND, proportion=1)
        self.btn_sizer.Add(self.btn_ok, flag=wx.LEFT, border=5)
        self.btn_sizer.Add(self.btn_cancel, flag=wx.LEFT, border=5)

        border = 0 if is_read_only else 10
        self.main_sizer.Add(self.top_sizer, flag=wx.ALL | wx.EXPAND, border=border)
        self.main_sizer.Add(self.mid_sizer, flag=wx.ALL | wx.EXPAND, border=border, proportion=1)
        self.main_sizer.Add(self.static_line, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=border)
        self.main_sizer.Add(self.btn_sizer, flag=wx.ALL | wx.EXPAND, border=border)

        self.change_layout(self.is_read_only)

        self.SetBackgroundColour(self.sep.GetBackgroundColour())
        self.SetSizer(self.main_sizer)

        self.Bind(wx.EVT_CLOSE, self.on_close, id=wx.ID_CANCEL)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_close, id=wx.ID_CANCEL)

    def on_close(self, e):
        self.Destroy()

    def change_layout(self, is_read_only):
        self.top_sizer.ShowItems(not is_read_only)
        self.static_line.Show(not is_read_only)
        self.btn_sizer.ShowItems(not is_read_only)

    def show(self):
        # self.main_sizer.Fit(self)
        # self.SetSize(self.GetEffectiveMinSize())
        _left, _top = self.frame.GetPosition()
        _width, _height = self.frame.GetSize()
        if self.is_left:
            self.SetPosition((_left - self.GetSize().GetWidth(), _top))
        else:
            self.SetPosition((_left + _width, _top))
        return self.Show()


class LinkDlg(SimpleMiniFrame):
    def __init__(self, frame, is_left, is_read_only, link_pages=None):
        super().__init__(frame, is_left, is_read_only)
        self.link_pages = link_pages if link_pages else LinkPages()
        self.page_ctrl = LinkPageCtrl(self, frame)
        self.page_ctrl.load_pages(self.link_pages.pages)
        self.mid_sizer.Add(self.page_ctrl, flag=wx.EXPAND, proportion=1)


class LinkPageCtrl(wx.Treebook):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        # self.GetTreeCtrl().SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION))
        self.frame = frame
        self.GetTreeCtrl().SetImageList(frame.im_list)

    def load_pages(self, pages):
        for page in pages:
            self.insert_page(0, page.page_name, page.page_items)

    def insert_page(self, pagePos, name, items):
        page = LinkPanel(self, self.frame, items)
        self.InsertPage(pagePos=pagePos, page=page, text=name, imageId=self.frame.img_parent)

    def insert_subpage(self, pagePos, name, items):
        page = LinkPanel(self, self.frame, items)
        self.InsertSubPage(pagePos=pagePos, page=page, text=name, imageId=self.frame.img_child)


class LinkPanel(wx.Panel):
    def __init__(self, parent, frame, items=[]):
        super().__init__(parent=parent)
        self.frame = frame
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.link_ctrl = LinkCtrl(self, frame, items)
        self.main_sizer.Add(self.link_ctrl, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(self.main_sizer)


class LinkCtrl(wx.ListCtrl):
    def __init__(self, parent, frame, items=[]):
        super().__init__(parent=parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER)
        # self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION))
        self.frame = frame
        self.SetImageList(frame.im_list, wx.IMAGE_LIST_SMALL)
        self.AppendColumn("Name")
        self.AppendColumn("Description")
        self.AppendColumn("Target")
        for item in items:
            row = self.Append([item.name, item.desc, item.target])

            self.SetItemImage(row, self.frame.img_link_folder)



