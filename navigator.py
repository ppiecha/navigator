import wx
from gui import main_frame as mf
from time import perf_counter


class Navigator(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.frame = mf.MainFrame()
        self.frame.Show()


if __name__ == '__main__':
    start = perf_counter()
    app = Navigator()
    app.frame.show_message(f"Load time {round(perf_counter() - start, 5)} secs")
    app.MainLoop()
