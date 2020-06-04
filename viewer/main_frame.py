import sys
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
        self.process_args()

    def process_args(self):
        if len(sys.argv) > 1:
            opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
            args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
            if args:
                self.editor.LoadFile(args[0])
                if "-r" in opts:
                    self.editor.SetReadOnly(True)