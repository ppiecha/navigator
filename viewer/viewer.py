import wx
import main_frame as mf


class Navigator(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.frame = mf.MainFrame()
        self.frame.Show()


if __name__ == '__main__':
    app = Navigator()
    app.MainLoop()