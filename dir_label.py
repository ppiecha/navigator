import wx
from pathlib import Path
import os
import subprocess
import constants as cn


class DirLabel(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.path_panel = parent
        self.browser_panel = parent.parent
        self.frame = frame
        self._dir_path = None
        self.dir_label = None
        self.label_top = None
        self.prefix = None
        self.selected = None
        self.suffix = None
        self.def_font = None
        self.link_font = None

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.on_focus_lost)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_focus_lost)
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_menu)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)

        wx.CallAfter(self.init)

    def reset(self):
        self.prefix = ""
        self.selected = ""
        self.suffix = ""
        self.Refresh()

    def AcceptsFocus(self):
        return False

    def on_focus_lost(self, e):
        self.reset()

    def open_dir(self, dir):
        self.browser_panel.browser.open_dir(dir_name=dir, sel_dir=cn.CN_GO_BACK)

    def on_left_down(self, event):

        def get_selected_path():
            if not self.prefix:
                return self.selected
            elif not self.suffix:
                return self.dir_path
            else:
                return self.dir_path[:self.dir_path.find(self.suffix)]

        if self.selected and "..." not in self.selected:
            dir = get_selected_path()
            if dir != self.dir_path:
                self.open_dir(dir)
                self.dir_path = dir
                self.suffix = ""
                self.Refresh()
        event.Skip()

    def on_size(self, e):
        self.dir_path = self._dir_path

    def on_menu(self, event):
        menu = PathMenu(self.frame, self.path_panel, self)
        self.frame.PopupMenu(menu)
        del menu

    def init(self):
        self.def_font = self.GetFont()
        self.link_font = wx.Font(self.def_font).Underlined()

    def on_mouse_move(self, event):
        x, y = event.GetPosition()
        prefix, selected, suffix = self.hit_test(x, y)
        if self.selected != selected:
            self.prefix = prefix
            self.selected = selected
            self.suffix = suffix
            # print(prefix, selected, suffix)
            self.Refresh()

        event.Skip()

    def set_value(self, value):
        self.dir_path = value

    @property
    def dir_path(self):
        return self._dir_path

    @dir_path.setter
    def dir_path(self, value):
        if not value:
            return
        if value == self._dir_path:
            return
        self._dir_path = value
        path = Path(value)
        prefix_len = wx.WindowDC(self).GetTextExtent(path.anchor).GetWidth()
        self.dir_label = path.anchor + wx.Control.Ellipsize(str(path)[len(path.anchor):], wx.WindowDC(self),
                                                            wx.ELLIPSIZE_START, self.GetSize().GetWidth() - prefix_len)
        self.Refresh()

    def hit_test(self, x, y):
        if not self.label_top or y <= self.label_top or y >= self.GetSize().GetHeight() - self.label_top:
            return self.dir_label, "", ""
        path = Path(self.dir_label)
        parts = path.parts
        dc = wx.WindowDC(self)
        prefix = ""
        selected = ""
        suffix = ""
        found = False
        for part in parts:
            if not found:
                if x - dc.GetTextExtent(os.path.join(prefix, part)).GetWidth() < 0:
                    # print(str(x - dc.GetTextExtent(os.path.join(prefix, part)).GetWidth()))
                    selected = part
                    found = True
                else:
                    prefix = os.path.join(prefix, part)
            else:
                suffix = os.path.join(suffix, part)
        if selected:
            return prefix, selected, suffix
        else:
            return prefix, "", ""

    def OnPaint(self, e):
        dc = wx.BufferedPaintDC(self)
        self.draw(dc)

    def draw(self, dc):
        # Background
        brush = wx.Brush(self.GetBackgroundColour())
        dc.SetBackground(brush)
        dc.Clear()
        # Text
        size = dc.GetTextExtent(self.dir_label)
        self.label_top = (self.GetSize().GetHeight() - size.GetHeight()) / 2
        start = 0
        if self.selected:
            if self.prefix:
                dc.SetFont(self.def_font)
                text = self.prefix + os.path.sep if not self.prefix.endswith(os.path.sep) else self.prefix
                dc.DrawText(text, start, self.label_top)
                start += dc.GetTextExtent(text).GetWidth()
            dc.SetFont(self.link_font)
            dc.DrawText(self.selected, start, self.label_top)
            start += dc.GetTextExtent(self.selected).GetWidth()
            if self.suffix:
                dc.SetFont(self.def_font)
                text = os.path.sep + self.suffix if not self.selected.endswith(os.path.sep) else self.suffix
                dc.DrawText(text, start, self.label_top)
        else:
            dc.DrawText(self.dir_label, 0, self.label_top)


CN_EDIT = "Edit"
CN_COPY = "Copy path to clipboard"
CN_CMD = "Run command prompt"
CN_MENU = "Show context menu"


class PathMenu(wx.Menu):
    def __init__(self, frame, path_panel, path_label):
        super().__init__()
        self.frame = frame
        self.path_panel = path_panel
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
            self.path_panel.read_only = False
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

