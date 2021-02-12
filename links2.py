import wx
from pathlib import Path
from typing import Dict
import config
import constants as cn
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


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
                         style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX, size=(600, 400))
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
        if self.is_left:
            self.frame.app_conf.left_assistant_rect = (self.GetRect())
        else:
            self.frame.app_conf.right_assistant_rect = (self.GetRect())
        self.Destroy()

    def change_layout(self, is_read_only):
        self.top_sizer.ShowItems(not is_read_only)
        self.static_line.Show(not is_read_only)
        self.btn_sizer.ShowItems(not is_read_only)

    def show(self):
        # self.main_sizer.Fit(self)
        # self.SetSize(self.GetEffectiveMinSize())
        if not self.frame.app_conf.left_assistant_rect:
            _left, _top = self.frame.GetPosition()
            _width, _height = self.frame.GetSize()
            if self.is_left:
                self.SetPosition((_left - self.GetSize().GetWidth(), _top))
            else:
                self.SetPosition((_left + _width, _top))
        else:
            if self.is_left:
                self.SetRect(self.frame.app_conf.left_assistant_rect)
            else:
                self.SetRect(self.frame.app_conf.left_assistant_rect)
        return self.Show()


class LinkDlg(SimpleMiniFrame):
    def __init__(self, frame, is_left, is_read_only):
        super().__init__(frame, is_left, is_read_only)
        self.page_ctrl = LinkPageCtrl(self, frame)
        # self.page_ctrl.load_pages(self.link_pages.pages)
        self.mid_sizer.Add(self.page_ctrl, flag=wx.EXPAND, proportion=1)

    def show(self):
        self.page_ctrl.SetSelection(0)
        self.page_ctrl.hist_page.SetSelection(0)
        self.page_ctrl.hist_page.folder_page.search_edit.SetFocus()
        super().show()


class LinkPageCtrl(wx.Simplebook):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.frame = frame
        self.hist_page = FilesFoldersPageCtrl(parent=self, frame=frame)
        self.AddPage(page=self.hist_page, text="History", select=True)
        # self.GetTreeCtrl().SetImageList(frame.im_list)

    # def load_pages(self, pages):
    #     for page in pages:
    #         self.insert_page(0, page.page_name, page.page_items)
    #
    # def insert_page(self, pagePos, name, items):
    #     page = LinkPanel(self, self.frame, items)
    #     self.InsertPage(pagePos=pagePos, page=page, text=name, imageId=self.frame.img_parent)
    #
    # def insert_subpage(self, pagePos, name, items):
    #     page = LinkPanel(self, self.frame, items)
    #     self.InsertSubPage(pagePos=pagePos, page=page, text=name, imageId=self.frame.img_child)


class FilesFoldersPageCtrl(wx.Notebook):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)#, style=wx.NB_BOTTOM)
        self.frame = frame
        self.folder_page = ListPanel(parent=self, frame=frame, source=self.frame.app_conf.folder_hist)
        self.file_page = ListPanel(parent=self, frame=frame, source=self.frame.app_conf.file_hist)
        self.AddPage(page=self.folder_page, text="Folders", select=True)
        self.AddPage(page=self.file_page, text="Files", select=False)
        # self.GetTreeCtrl().SetImageList(frame.im_list)


class ListPanel(wx.Panel):
    def __init__(self, parent, frame, source):
        super().__init__(parent=parent)
        self.frame = frame
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_edit = wx.SearchCtrl(parent=self, style=wx.WANTS_CHARS)
        self.h_sizer.Add(wx.StaticText(parent=self, label="Search: "),
                         flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT,
                         border=2)
        self.h_sizer.Add(self.search_edit)
        self.list_ctrl = LinkList(self, frame=frame, source=source)

        self.main_sizer.Add(self.h_sizer)
        self.main_sizer.Add(self.list_ctrl, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(self.main_sizer)

        self.search_edit.Bind(wx.EVT_TEXT, self.on_search)
        self.search_edit.Bind(wx.EVT_CHAR, self.on_key_down)

    def on_search(self, e):
        self.list_ctrl.filter_list(self.search_edit.GetValue())

    def on_key_down(self, e):
        if e.GetKeyCode() in [wx.WXK_UP, wx.WXK_DOWN]:
            self.list_ctrl.SetFocus()
        e.Skip()


class LinkList(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent, frame, source: Dict[str, config.HistItem]):
        super().__init__(parent=parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL) # | wx.LC_NO_HEADER)
        ListCtrlAutoWidthMixin.__init__(self)
        # self.setResizeColumn(0)
        # self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION))
        self.frame = frame
        self.source = source
        self.filtered_dict: Dict[str, config.HistItem] = {}
        self.SetImageList(frame.im_list, wx.IMAGE_LIST_SMALL)
        self.AppendColumn("Name")
        self.AppendColumn("Source")
        self.filter_list(filter="")

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.on_start_drag)

    def filter_list(self, filter: str) -> None:

        if filter == "":
            self.filtered_dict = self.source
        else:
            self.filtered_dict = {k: v for k, v in self.source.items() if filter.lower() in k.lower()}
        self.DeleteAllItems()
        for k, v in sorted(self.filtered_dict.items(), key=lambda item: item[0]):
            path = Path(v.full_path)
            row = self.Append([v.name, v.full_path])
            self.SetItemImage(row,
                              self.frame.img_folder if path.is_dir() else self.frame.get_ext_image_id(path.suffix))

    def go_to_path(self, path: Path):
        self.frame.return_focus()
        self.frame.get_active_win().get_active_browser().open_dir(dir_name=path.parent,
                                                                  sel_dir=path.name)

    def on_item_activated(self, e):
        row = self.GetFirstSelected()
        if row >= 0:
            item_name = self.GetItemText(row, 1)
            path = Path(item_name)
            if wx.GetKeyState(wx.WXK_CONTROL) and wx.GetKeyState(wx.WXK_SHIFT):
                if Path(item_name).is_dir():
                    self.frame.get_inactive_win().add_new_tab(item_name)
                else:
                    pass
            elif wx.GetKeyState(wx.WXK_CONTROL):
                if Path(item_name).is_dir():
                    self.frame.get_active_win().add_new_tab(item_name)
                else:
                    pass
            else:
                if Path(item_name).is_dir():
                    self.frame.get_active_win().get_active_browser().open_dir(dir_name=item_name)
                else:
                    # self.res_frame.nav_frame.return_focus()
                    self.frame.get_active_win().get_active_browser().open_dir(dir_name=path.parent,
                                                                              sel_dir=path.name)

    def on_start_drag(self, e):
        selected = e.GetItem()
        if not selected:
            return
        files = wx.FileDataObject()
        files.AddFile(self.GetItemText(selected.GetId(), 1))
        drag_src = wx.DropSource(win=self.frame, data=files)
        result = drag_src.DoDragDrop()
