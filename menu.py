import wx
import constants as cn


# FILE
NEW_FILE = "New file"
RENAME = "Rename"
VIEW = "View"
EDIT = "Edit"
COPY = "Copy"
MOVE = "Move"
NEW_FOLDER = "New folder"
DELETE = "Delete"
EXIT = "Exit"

# EDIT
SELECT_ALL = "Select all"
INVERT_SEL = "Invert selection"

COPY_PATH = "Copy path"
COPY_SEL_NAMES = "Copy selected names"
COPY_SEL_NAMES_AND_PATHS = "Copy selected names with path"


class MainMenu(wx.MenuBar):
    def __init__(self, frame):
        super().__init__()
        self.file_lst = [
            [NEW_FILE, wx.ITEM_NORMAL, wx.WXK_F9, wx.ACCEL_NORMAL, None], #wx.Bitmap(cn.CN_IM_RENAME, wx.BITMAP_TYPE_PNG)],
            [RENAME, wx.ITEM_NORMAL, wx.WXK_F2, wx.ACCEL_NORMAL, None], #wx.Bitmap(cn.CN_IM_RENAME, wx.BITMAP_TYPE_PNG)],
            [VIEW, wx.ITEM_NORMAL, wx.WXK_F3, wx.ACCEL_NORMAL, None], #wx.Bitmap(cn.CN_IM_VIEWER, wx.BITMAP_TYPE_PNG)],
            [EDIT, wx.ITEM_NORMAL, wx.WXK_F4, wx.ACCEL_NORMAL, None], #wx.Bitmap(cn.CN_IM_EDIT, wx.BITMAP_TYPE_PNG)],
            [COPY, wx.ITEM_NORMAL, wx.WXK_F5, wx.ACCEL_NORMAL, None], #wx.Bitmap(cn.CN_IM_COPY, wx.BITMAP_TYPE_PNG)],
            [MOVE, wx.ITEM_NORMAL, wx.WXK_F6, wx.ACCEL_NORMAL, None], #wx.Bitmap(cn.CN_IM_MOVE, wx.BITMAP_TYPE_PNG)],
            [NEW_FOLDER, wx.ITEM_NORMAL, wx.WXK_F7, wx.ACCEL_NORMAL,
             None], #wx.Bitmap(cn.CN_IM_NEW_FOLDER, wx.BITMAP_TYPE_PNG)],
            [DELETE, wx.ITEM_NORMAL, wx.WXK_F8, wx.ACCEL_NORMAL, None], #wx.Bitmap(cn.CN_IM_DELETE, wx.BITMAP_TYPE_PNG)],
            ["-", wx.ITEM_SEPARATOR, None, None, None],
            [EXIT, wx.ITEM_NORMAL, wx.WXK_F4, wx.ACCEL_ALT, None]
        ]
        self.edit_lst = [
            [SELECT_ALL, wx.ITEM_NORMAL, ord("A"), wx.ACCEL_CTRL, None],
            [INVERT_SEL, wx.ITEM_NORMAL, ord("A"), wx.ACCEL_SHIFT + wx.ACCEL_CTRL, None],
            ["-", wx.ITEM_SEPARATOR, None, None, None],
            [COPY_PATH, wx.ITEM_NORMAL, wx.WXK_F4, wx.ACCEL_NORMAL, None],
            [COPY_SEL_NAMES, wx.ITEM_NORMAL, wx.WXK_F5, wx.ACCEL_NORMAL, None],
            [COPY_SEL_NAMES_AND_PATHS, wx.ITEM_NORMAL, wx.WXK_F6, wx.ACCEL_NORMAL, None],
            # [NEW_FOLDER, wx.ITEM_NORMAL, wx.WXK_F7, wx.ACCEL_NORMAL, None],
            # [DELETE, wx.ITEM_NORMAL, wx.WXK_F8, wx.ACCEL_NORMAL, None],
            # ["-", wx.ITEM_SEPARATOR, None, None, None],
            # [EXIT, wx.ITEM_NORMAL, wx.WXK_F4, wx.ACCEL_ALT, None]
        ]
        self.frame = frame
        self.menu_items_id = {}
        self.entries = []

        self.file_menu = wx.Menu()
        self.create_menu(self.file_menu, self.file_lst)
        self.edit_menu = wx.Menu()
        self.create_menu(self.edit_menu, self.edit_lst)

        self.Append(self.file_menu, '&File')
        self.Append(self.edit_menu, '&Edit')

        self.frame.SetAcceleratorTable(wx.AcceleratorTable(self.entries))

    def create_menu(self, menu, lst):
        for item in lst:
            self.menu_items_id[wx.NewId()] = item
        for id in self.menu_items_id.keys():
            if self.menu_items_id[id][0] in [i[0] for i in lst]:
                new_menu_item = menu.Append(id, item=self.menu_items_id[id][0], kind=self.menu_items_id[id][1])
                if new_menu_item.GetItemLabelText() != "-":
                    entry = wx.AcceleratorEntry(self.menu_items_id[id][3], self.menu_items_id[id][2], id, new_menu_item)
                    new_menu_item.SetAccel(entry)
                    self.entries.append(entry)
                    self.Bind(wx.EVT_MENU, self.on_click, id=id)
                    # if self.menu_items_id[id][4]:
                    #     self.frame.tb.AddTool(toolId=id, label=self.menu_items_id[id][0], bitmap=self.menu_items_id[id][4])
                    #     self.Bind(wx.EVT_TOOL, self.OnToolClick, id=id)
                    # self.frame.tb.Realize()

    def on_click(self, event):
        operation = self.menu_items_id[event.GetId()][0]
        # File
        if operation == NEW_FILE:
            self.frame.new_file()
        elif operation == RENAME:
            self.frame.rename()
        elif operation == NEW_FOLDER:
            self.frame.new_folder()
        elif operation == VIEW:
            self.frame.view()
        elif operation == DELETE:
            self.frame.delete()
        # Edit
        if operation == SELECT_ALL:
            self.frame.select_all()
        if operation == INVERT_SEL:
            self.frame.invert_selection()
