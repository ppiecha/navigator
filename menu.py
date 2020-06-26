import wx
import constants as cn


# EDIT
SELECT_ALL = "Select all"
INVERT_SEL = "Invert selection"

COPY_PATH = "Copy path"
COPY_SEL_NAMES = "Copy selected names"
COPY_SEL_NAMES_AND_PATHS = "Copy selected names with path"


class MainMenu(wx.MenuBar):
    def __init__(self, frame):
        super().__init__()

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
        self.entries.append(wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_DELETE, cn.ID_DELETE))
        self.file_menu = wx.Menu()
        self.make_menu(self.file_menu, cn.dt_file)
        self.edit_menu = wx.Menu()
        self.make_menu(self.edit_menu, cn.dt_edit)

        self.Append(self.file_menu, '&File')
        self.Append(self.edit_menu, '&Edit')

    def make_menu(self, menu_item, menu_dict):
        for id in menu_dict.keys():
            item = wx.MenuItem(id=id, text=menu_dict[id].name, kind=menu_dict[id].type)
            if not menu_dict[id].hidden:
                menu_item.Append(item)
            if menu_dict[id].name != "-":
                if menu_dict[id].hidden:
                    entry = wx.AcceleratorEntry(menu_dict[id].acc_type, menu_dict[id].key, id)
                else:
                    entry = wx.AcceleratorEntry(menu_dict[id].acc_type, menu_dict[id].key, id, item)
                    item.SetAccel(entry)
                self.entries.append(entry)
                self.Bind(wx.EVT_MENU, self.on_click, id=id)

    def exec_cmd_id(self, id):
        # File
        if id == cn.ID_RENAME:
            self.frame.rename()
        elif id == cn.ID_VIEW:
            self.frame.view()
        elif id == cn.ID_EDIT:
            self.frame.view()
        elif id == cn.ID_COPY:
            self.frame.copy()
        elif id == cn.ID_MOVE:
            self.frame.move()
        elif id == cn.ID_NEW_FOLDER:
            self.frame.new_folder()
        elif id == cn.ID_DELETE:
            self.frame.delete(None)
        elif id == cn.ID_NEW_FILE:
            self.frame.new_file()
        elif id == cn.ID_CREATE_SHORTCUT:
            self.frame.on_create_shortcut(None)
        elif id == cn.ID_COPY2SAME:
            self.frame.on_copy2same(None)
        elif id == cn.ID_COPY_CLIP:
            self.frame.copy_file2clip(None)
        elif id == cn.ID_PASTE_CLIP:
            self.frame.paste_files_from_clip(None)
        # Edit
        elif id == cn.ID_SELECT_ALL:
            self.frame.select_all()
        elif id == cn.ID_INVERT_SEL:
            self.frame.invert_selection()
        elif id == cn.ID_COPY_SEL_NAMES:
            self.frame.copy_sel2clip()
        elif id == cn.ID_COPY_SEL_NAMES_AND_PATHS:
            self.frame.copy_sel2clip_with_path()


    def on_click(self, event):
        self.exec_cmd_id(event.GetId())

