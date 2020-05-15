import wx
import os
import constants as cn
import subprocess
from pathlib import Path
import util


class PathLabel(wx.TextCtrl):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.frame = frame
        self._read_only = True
        self.read_only = True

        self.AutoCompleteDirectories()
        self.AutoCompleteFileNames()

        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, e):
        e.Skip()
        self.SetValue(self.get_shortcut(self.get_current_dir()))

    def get_shortcut(self, text):
        path = Path(text)
        anchor = path.anchor
        rest = self.Ellipsize(str(path)[len(anchor):], wx.ClientDC(self), wx.ELLIPSIZE_START,
                              self.GetSize().GetWidth() - 30)
        return os.path.join(anchor, rest)

    def on_key_down(self, event):
        if self.read_only:
            return
        else:
            event.Skip()
            if event.GetKeyCode() == wx.WXK_RETURN:
                path = Path(self.GetValue())
                if path.exists():
                    if path.is_dir():
                        if not path.samefile(Path(self.get_current_dir())):
                            self.open_dir(path)
                            if not str(path).endswith(os.path.sep):
                                self.SetValue(str(path) + os.path.sep)
                    else:
                        self.open_file(path)
                else:
                    # args = self.GetValue().split()
                    # result = subprocess.Popen(args, shell=True)
                    result = wx.Execute(self.GetValue())
                    # if not result:
                    #     self.frame.show_message("Cannot execute command")
                    # output, error = result.communicate()
                    # print(output, error)
                self.SelectNone()
                self.SetInsertionPointEnd()

    def open_dir(self, dir):
        self.parent.parent.browser.open_dir(dir_name=dir, sel_dir=cn.CN_GO_BACK)

    def open_file(self, file_name):
        self.parent.parent.browser.open_file(file_name)

    def context_menu(self, path, item_names):
        self.parent.parent.browser.get_context_menu(path, item_names)

    def get_current_dir(self):
        if hasattr(self.parent.parent, 'browser'):
            return str(self.parent.parent.browser.path)
        else:
            return ""

    def on_menu(self, event):
        # self.SelectAll()
        menu = PathMenu(self.frame, self)
        self.frame.PopupMenu(menu)

    def on_left_down(self, event):
        if self.read_only and self.GetStringSelection():
            end = self.get_current_dir().find(self.GetStringSelection()) + len(self.GetStringSelection())
            self.open_dir(self.get_current_dir()[:end+1])
        event.Skip()

    def on_enter_window(self, event):
        # self.SetFocus()
        pass

    def on_kill_focus(self, event):
        self.read_only = True
        event.Skip()

    def on_mouse_move(self, event):

        def get_text_to_select(parts, pos):
            counter = 0
            for id, part in enumerate(parts):
                counter += len(part) + 1
                if counter > pos:
                    return parts[id]

        if self.read_only and not wx.GetMouseState().LeftIsDown():
            x, y = event.GetPosition()
            path = self.GetValue()
            row, col = self.HitTestPos((x, y))
            parts = path.split(os.path.sep)
            selection = get_text_to_select(parts, col)
            start = path.find(selection)
            if start > -1 and not path.endswith(selection) and selection.find("...") == -1:
                self.SetFocus()
                self.SetSelection(start, start + len(selection))
            else:
                self.SelectNone()

        event.Skip()


    @property
    def read_only(self):
        return self._read_only

    @read_only.setter
    def read_only(self, value):
        self.SetEditable(not value)
        if value:
            self.HideNativeCaret()
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
            self.Bind(wx.EVT_CONTEXT_MENU, self.on_menu)
            if self.get_current_dir():
                self.SetValue(self.get_shortcut(self.get_current_dir()))
            self.SelectNone()
        else:
            self.ShowNativeCaret()
            self.SetCursor(wx.Cursor(wx.CURSOR_IBEAM))
            res = self.Unbind(wx.EVT_CONTEXT_MENU)
            print(res)
            self.SelectAll()
        self._read_only = value


CN_EDIT = "Edit"
CN_COPY = "Copy path to clipboard"
CN_CMD = "Run command prompt"
CN_MENU = "Show context menu"


class PathMenu(wx.Menu):
    def __init__(self, frame, path_label):
        super().__init__()
        self.frame = frame
        self.path_label = path_label
        self.menu_items = [CN_EDIT, CN_MENU, CN_COPY, CN_CMD]
        self.menu_items_id = {}
        for item in self.menu_items:
            self.menu_items_id[wx.NewId()] = item
        for id in self.menu_items_id.keys():
            self.Append(id, item=self.menu_items_id[id])
            self.Bind(wx.EVT_MENU, self.on_click, id=id)

    def on_click(self, event):
        operation = self.menu_items_id[event.GetId()]
        if operation == CN_EDIT:
            self.path_label.read_only = False
        elif operation == CN_COPY:
            self.path_label.Copy()
        elif operation == CN_CMD:
            subprocess.Popen(["start", "cmd"], shell=True)
        elif operation == CN_MENU:
            path = Path(self.path_label.GetValue())
            print(path.parent)
            self.path_label.context_menu("C:", [])
            # path = Path(self.path_label.GetValue())
            # if path.exists():
            #     self.path_label.context_menu(path.parent, [path.name])


class HistMenu(wx.Menu):
    def __init__(self):
        super().__init__()
        self.browser = None
        self.sorted_items = []
        self.sorted_items_id = {}

    def set_browser(self, browser):
        self.browser = browser

    def update(self):
        for item in self.GetMenuItems():
            self.Delete(item)
        self.sorted_items = sorted(self.browser.history)
        self.sorted_items_id = {}
        for item in self.sorted_items:
            self.sorted_items_id[wx.NewId()] = item
        for id in self.sorted_items_id.keys():
            self.Append(id, item=self.sorted_items_id[id])
            self.Bind(wx.EVT_MENU, self.on_click, id=id)

    def on_click(self, event):
        operation = self.sorted_items_id[event.GetId()]
        self.browser.open_dir(operation)


class PathPanel(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame
        self.drive_combo = DriveCombo(self, self.frame)
        self.path_lbl = PathLabel(self, self.frame)
        self.fav_btn = PathBtn(self, cn.CN_IM_FAV)
        self.hist_btn = PathBtn(self, cn.CN_IM_HIST)
        self.hist_menu = HistMenu()
        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.sizer_h.Add(self.drive_combo)
        self.sizer_h.Add(self.fav_btn)
        self.sizer_h.Add(self.hist_btn)
        self.sizer_v.Add(self.path_lbl, flag=wx.EXPAND, proportion=1)
        self.sizer_v.Add(self.sizer_h, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(self.sizer_v)

        self.hist_btn.Bind(wx.EVT_BUTTON, self.on_history)
        self.fav_btn.Bind(wx.EVT_BUTTON, self.on_favorite)

    def AcceptsFocusFromKeyboard(self):
        return False

    def on_favorite(self, e):
        self.parent.browser.select_first_one()

    def on_history(self, event):
        self.hist_menu.update()
        self.frame.PopupMenu(self.hist_menu)


class DriveCombo(wx.ComboBox):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, choices=util.get_drives(), style=wx.CB_READONLY | wx.CB_SORT, size=(40, 23))
        self.parent = parent

        self.Bind(wx.EVT_COMBOBOX, self.on_select)

    def on_select(self, event):
        self.parent.path_lbl.open_dir(event.GetString())


class PathBtn(wx.BitmapButton):
    def __init__(self, parent, image):
        super().__init__(parent=parent, bitmap=wx.Bitmap(image, wx.BITMAP_TYPE_PNG), size=(23, 23))


