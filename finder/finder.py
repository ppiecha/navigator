import wx
from gui import main_frame as mf
import res_frame as rf


class Navigator(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.frame = mf.MainFrame(app=self)
        self.frame.res_frame = rf.MainFrame(self.frame)
        self.frame.Show()

if __name__ == '__main__':
    app = Navigator()
    app.MainLoop()