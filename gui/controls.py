from __future__ import annotations
import wx
import wx.lib.buttons as buttons
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


class FileNameEdit(wx.TextCtrl):
    def __init__(self, parent, value, size):
        super().__init__(parent=parent, value=value, size=size)

    def smart_select(self):
        path, sep, name = self.GetValue().rpartition(os.path.sep)
        name, dot, ext = name.partition(".")
        if dot:
            self.SetSelection(len(path) + len(sep), len(path) + len(sep) + len(name))
        elif not path:
            self.SelectAll()


class ToolBtn(buttons.ThemedGenBitmapButton):
    def __init__(self, parent, im_file, def_ctrl=[], size=(24, 24)):
        super().__init__(parent, -1, wx.Bitmap(im_file, wx.BITMAP_TYPE_PNG), size=size)
        self.def_ctrl = def_ctrl
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)

    def AcceptsFocusFromKeyboard(self):
        return False

    def on_focus(self, event):
        if self.def_ctrl:
            self.def_ctrl[0].SetFocus()
            return
        event.Skip()

    def SetBitmap(self, pic):
        self.SetBitmapLabel(pic)
        self.Refresh()

    def set_bitmap(self, im_file):
        self.SetBitmapLabel(wx.Bitmap(im_file, wx.BITMAP_TYPE_PNG))
        self.Refresh()

    def set_off_bitmap(self, im_file):
        self.SetBitmapDisabled(wx.Bitmap(im_file, wx.BITMAP_TYPE_PNG))


class ToggleBtn(wx.BitmapToggleButton):
    def __init__(self, parent, im_file_off, im_file_on, def_ctrl=[], size=(24, 24)):
        super().__init__(parent, -1, wx.Bitmap(im_file_off, wx.BITMAP_TYPE_PNG), size=size)
        self.SetBitmapPressed(wx.Bitmap(im_file_on, wx.BITMAP_TYPE_PNG))
        self.def_ctrl = def_ctrl

        # self.Bind(wx.EVT_SET_FOCUS, self.on_focus)

    def AcceptsFocus(self):
        return False

    def on_focus(self, event):
        if self.def_ctrl:
            self.def_ctrl[0].SetFocus()
        event.Skip()

    def set_bitmap(self, im_file):
        self.SetBitmapLabel(wx.Bitmap(im_file, wx.BITMAP_TYPE_PNG))
        self.Refresh()

    def set_off_bitmap(self, im_file):
        self.SetBitmapDisabled(wx.Bitmap(im_file, wx.BITMAP_TYPE_PNG))


class CmdBtn(wx.Button):
    def __init__(self, parent, id, label, size):
        super().__init__(parent=parent, id=id, label=label, size=size)
        self.frame = parent
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)

    def AcceptsFocus(self):
        return False

    def AcceptsFocusFromKeyboard(self):
        return False

    def on_focus(self, e):
        self.frame.return_focus()
        self.frame.menu_bar.exec_cmd_id(self.GetId())


class PathBtn(wx.BitmapButton):
    def __init__(self, parent, frame, image):
        super().__init__(parent=parent, bitmap=wx.Bitmap(image, wx.BITMAP_TYPE_PNG), size=(23, 23))
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.frame = frame

    def on_focus(self, e):
        if hasattr(self.frame, 'return_focus'):
            self.frame.return_focus()

    def AcceptsFocusFromKeyboard(self):
        return False

    def AcceptsFocus(self):
        return False


class NoFocusImgBtn(wx.BitmapButton):
    def __init__(self, parent, image: str, callable=None, def_ctrl=None, exe_call: bool = True) -> None:
        super().__init__(parent=parent, bitmap=wx.Bitmap(image, wx.BITMAP_TYPE_PNG), size=(23, 23))
        self.callable = callable
        self.exe_call = exe_call
        self.def_ctrl = def_ctrl

        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)

    def on_focus(self, e):
        # if self.exe_call:
        #     self.callable()
        if self.def_ctrl is not None:
            self.def_ctrl.SetFocus();

    def AcceptsFocusFromKeyboard(self):
        return False

    def AcceptsFocus(self):
        return False
