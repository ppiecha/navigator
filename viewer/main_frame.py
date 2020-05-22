import wx
import editor

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Viewer", size=(395, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.main_panel = MainPanel(frame=self)

        self.Center()


class MainPanel(wx.Panel):
    def __init__(self, frame):
        super().__init__(parent=frame)
        self.editor = editor.Editor(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.editor, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(sizer)