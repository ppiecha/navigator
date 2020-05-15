import wx
import controls
import constants as cn
import util


class DrivePnl(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self.parent = parent
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.drives = util.get_drives()
        self.buttons = {}
        for drive in self.drives:
            button = controls.DriveBtn(self, str(drive[0]).lower())
            button.Bind(wx.EVT_TOGGLEBUTTON, self.on_press)
            button.SetToolTip(drive)
            self.buttons[button] = drive
            self.sizer.Add(button)
        self.SetSizerAndFit(self.sizer)

    def on_press(self, event):
        self.parent.browser.conf.use_pattern = self.filter_btn.GetValue()
        self.parent.browser.do_search_folder(self.filter.GetValue())

    def set_def_ctrl(self, ctrl):
        for button in self.buttons.keys():
            button.set_def_ctrl(ctrl)
