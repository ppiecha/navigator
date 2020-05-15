import wx
import controls
import constants as cn


class FilterPnl(wx.Panel):
    def __init__(self, parent, frame, browser):
        super().__init__(parent)
        self.frame = frame
        self.parent = parent
        self.browser = browser
        self.sum_lbl = wx.StaticText(parent=self, label="BBB", style=wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE)
        self.filter = Filter(self, frame)
        self.filter_btn = controls.ToggleBtn(self, cn.CN_IM_FILTER_OFF, cn.CN_IM_FILTER, def_ctrl=[self.filter])
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.sum_lbl, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, proportion=1, border=5)
        self.sizer.Add(self.filter)
        self.sizer.Add(self.filter_btn)
        self.SetSizerAndFit(self.sizer)

        self.filter_btn.Bind(wx.EVT_TOGGLEBUTTON, self.on_press)
        self.filter.Bind(wx.EVT_TEXT, self.on_search)
        self.filter.Bind(wx.EVT_CHAR, self.on_key_down)

    def select_first_one(self):
        self.browser.select_first_one()

    def disable_filter(self, clear_search=False):
        self.filter_btn.SetValue(False)
        self.browser.conf.use_pattern = False
        if clear_search:
            self.filter.Clear()
        else:
            self.browser.do_search_folder(self.filter.GetValue())


    def enable_filter(self):
        self.filter.SetFocus()
        self.filter_btn.SetValue(True)
        self.browser.conf.use_pattern = True
        if self.filter.GetValue() != "":
            self.browser.do_search_folder(self.filter.GetValue())

    def AcceptsFocusFromKeyboard(self):
        return False

    def on_press(self, event):
        if self.filter.GetValue():
            self.browser.conf.use_pattern = self.filter_btn.GetValue()
            self.browser.do_search_folder(self.filter.GetValue())
        else:
            self.filter_btn.SetValue(False)

    def on_key_down(self, e):
        if e.GetKeyCode() != wx.WXK_ESCAPE:
            e.Skip()
        if e.GetKeyCode() in [wx.WXK_UP, wx.WXK_DOWN, wx.WXK_ESCAPE]:
            self.browser.select_first_one()
            self.browser.SetFocus()
            if e.GetKeyCode() == wx.WXK_ESCAPE:
                self.disable_filter()

    def on_search(self, event):
        # if self.filter.GetValue() != "":
        self.browser.conf.use_pattern = (self.filter.GetValue() != "")
        self.filter_btn.SetValue((self.filter.GetValue() != ""))
        self.browser.do_search_folder(event.GetString())
        event.Skip()


class Filter(wx.SearchCtrl):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, size=(60, 23), style=wx.WANTS_CHARS)
        self.frame = frame
        self.parent = parent
        self.ShowSearchButton(False)
        self.ShowCancelButton(False)


