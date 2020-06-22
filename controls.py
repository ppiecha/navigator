import wx
import wx.lib.buttons as buttons
import constants as cn


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


class DriveBtn(buttons.GenBitmapTextToggleButton):
    def __init__(self, parent, label):
        super().__init__(parent=parent, bitmap=wx.Bitmap(cn.CN_IM_DRIVE, wx.BITMAP_TYPE_PNG), size=(42, 24),
                         style=wx.BU_LEFT, label=label)
        self.def_ctrl = None

        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)

    def set_def_ctrl(self, ctrl):
        self.def_ctrl = [ctrl]

    def AcceptsFocus(self):
        return False

    def on_focus(self, event):
        if self.def_ctrl:
            self.def_ctrl[0].SetFocus()
        event.Skip()


class PathBtn(wx.BitmapButton):
    def __init__(self, parent, frame, image):
        super().__init__(parent=parent, bitmap=wx.Bitmap(image, wx.BITMAP_TYPE_PNG), size=(23, 23))
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.frame = frame

    def on_focus(self, e):
        if hasattr(self.frame, 'return_focus'):
            self.frame.return_focus()
        # e.Skip()

    def AcceptsFocusFromKeyboard(self):
        return False
