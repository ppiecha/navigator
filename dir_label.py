import wx
from pathlib import Path
import os
import subprocess
import constants as cn
import ctypes.wintypes


class DirLabel(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.path_panel = parent
        self.browser_panel = parent.parent
        self.frame = frame
        self._dir_path = None
        self.force = False
        self.last_label = ""
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
        self._refresh()

    def is_active(self):
        return self.browser_panel.browser.HasFocus()

    def AcceptsFocus(self):
        return False

    def on_focus_lost(self, e):
        self.reset()
        e.Skip()

    def open_dir(self, dir):
        self.browser_panel.browser.open_dir(dir_name=dir, sel_dir=cn.CN_GO_BACK)

    def get_selected_path(self):
        if not self.prefix:
            return self.selected
        elif not self.suffix:
            return self.dir_path
        else:
            return self.dir_path[:self.dir_path.find(self.suffix)]

    def on_left_down(self, event):
        self.browser_panel.browser.SetFocus()
        if self.selected and "..." not in self.selected:
            dir = self.get_selected_path()
            if dir != self.dir_path:
                self.open_dir(dir)
                self.dir_path = dir
                self.suffix = ""
                self._refresh()
        event.Skip()

    def on_size(self, e):
        self.dir_path = self._dir_path

    def on_menu(self, event):
        self.browser_panel.browser.SetFocus()
        menu = PathMenu(self.frame, self.path_panel, self, self.get_selected_path())
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
            self._refresh()

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
        # if value == self._dir_path:
        #     return
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

    def _refresh(self):
        self.force = True
        self.Refresh()

    def OnPaint(self, e):
        dc = wx.BufferedPaintDC(self)
        self.draw(dc)

    def draw(self, dc):
        if self.dir_label != self.last_label or self.selected or self.force:
            self.last_label = self.dir_label
            self.force = False
            # Background
            brush = wx.Brush(self.GetBackgroundColour())
            dc.SetBackground(brush)
            dc.Clear()
            # Text
            size = dc.GetTextExtent(self.dir_label)
            # self.label_top = (self.GetSize().GetHeight() - size.GetHeight()) / 2
            # print("label top", self.label_top)
            self.label_top = 1
            if self.is_active():
                brush = wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTACTIVECAPTION))
                pen = wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTACTIVECAPTION))
                dc.SetBrush(brush)
                dc.SetPen(pen)
                dc.DrawRectangle(0, self.label_top, self.GetSize().GetWidth(), size.GetHeight()+1)
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



CN_OPEN = "Open in new tab"
CN_OPEN_OW = "Open in new tab in opposite window"
CN_SEP = "-"
CN_EDIT = "Edit"
CN_COPY = "Copy full path to clipboard"
CN_CMD = "Run command prompt"
CN_DRIVE = "Show drive properties"


class PathMenu(wx.Menu):
    def __init__(self, frame, path_panel, path_label, selected_path):
        super().__init__()
        self.frame = frame
        self.path_panel = path_panel
        self.path_label = path_label
        self.selected_path = selected_path
        self.menu_items = [CN_OPEN, CN_OPEN_OW, CN_SEP, CN_EDIT, CN_COPY, CN_SEP, CN_CMD, CN_DRIVE]
        self.menu_items_id = {}
        for item in self.menu_items:
            self.menu_items_id[wx.NewId()] = item
        for id in self.menu_items_id.keys():
            if self.menu_items_id[id] == CN_SEP:
                self.AppendSeparator()
            else:
                item = self.Append(id, item=self.menu_items_id[id])
                self.Bind(wx.EVT_MENU, self.on_click, id=id)

    def on_click(self, event):
        operation = self.menu_items_id[event.GetId()]
        if operation == CN_OPEN:
            self.path_panel.parent.parent.add_new_tab(self.selected_path
                                                      if self.selected_path
                                                      else self.path_panel.path_edit.GetValue())
        elif operation == CN_OPEN_OW:
            self.frame.get_inactive_win().add_new_tab(self.selected_path
                                                      if self.selected_path
                                                      else self.path_panel.path_edit.GetValue())
        elif operation == CN_EDIT:
            self.path_panel.read_only = False
        elif operation == CN_COPY:
            self.frame.copy_text2clip([self.path_panel.path_edit.GetValue()])
        elif operation == CN_CMD:
            curr_path = os.getcwd()
            os.chdir(self.selected_path if self.selected_path else self.path_panel.path_edit.GetValue())
            subprocess.Popen(["start", "cmd"], shell=True)
            os.chdir(curr_path)
        elif operation == CN_DRIVE:
            self.show_drive_props(Path(self.path_panel.path_edit.GetValue()).anchor.rstrip("\\"))

    def show_drive_props(self, drive_nobackslash):
        sei = SHELLEXECUTEINFO()
        sei.cbSize = ctypes.sizeof(sei)
        sei.fMask = _SEE_MASK_NOCLOSEPROCESS | _SEE_MASK_INVOKEIDLIST
        sei.lpVerb = "properties"
        sei.lpFile = drive_nobackslash + '\\'
        sei.nShow = 1
        ShellExecuteEx(ctypes.byref(sei))


_SEE_MASK_NOCLOSEPROCESS = 0x00000040
_SEE_MASK_INVOKEIDLIST = 0x0000000C


class SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = (
        ("cbSize", ctypes.wintypes.DWORD),
        ("fMask", ctypes.c_ulong),
        ("hwnd", ctypes.wintypes.HANDLE),
        ("lpVerb", ctypes.c_wchar_p),
        ("lpFile", ctypes.c_wchar_p),
        ("lpParameters", ctypes.c_char_p),
        ("lpDirectory", ctypes.c_char_p),
        ("nShow", ctypes.c_int),
        ("hInstApp", ctypes.wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", ctypes.c_char_p),
        ("hKeyClass", ctypes.wintypes.HKEY),
        ("dwHotKey", ctypes.wintypes.DWORD),
        ("hIconOrMonitor", ctypes.wintypes.HANDLE),
        ("hProcess", ctypes.wintypes.HANDLE),
    )


ShellExecuteEx = ctypes.windll.shell32.ShellExecuteExW
ShellExecuteEx.restype = ctypes.wintypes.BOOL


