import wx
import constants as cn


class MainMenu(wx.MenuBar):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        self.save_project_item = None
        entries = []

        self.file_menu = wx.Menu()

        self.Append(self.file_menu, '&File')

        acc = wx.AcceleratorTable(entries)
        self.frame.SetAcceleratorTable(acc)