from datetime import datetime
from typing import Dict

import wx
import win32api
import win32gui
import win32con
import win32clipboard
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


class ClipFrame(wx.MiniFrame):
    def __init__(self, main_frame):
        wx.Frame.__init__(self, None, title="Clipboard viewer", size=(250, 250),
                          style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX)
        self.ToggleWindowStyle(wx.STAY_ON_TOP)
        if main_frame.app_conf.clip_view_rect:
            self.SetRect(main_frame.app_conf.clip_view_rect)
        self.clip_dict = {}

        self.first = True
        self.nextWnd = None

        # Get native window handle of this wxWidget Frame.
        self.hwnd = self.GetHandle()
        print(self.hwnd)

        # Set the WndProc to our function.
        self.oldWndProc = win32gui.SetWindowLong (self.hwnd,
                                                  win32con.GWL_WNDPROC,
                                                  self.MyWndProc)

        try:
            self.nextWnd = win32clipboard.SetClipboardViewer(self.hwnd)
        except win32api.error:
            if win32api.GetLastError () == 0:
                # information that there is no other window in chain
                pass
            else:
                raise
        self.cp = ClipPanel(parent=self, frame=main_frame, source=self.clip_dict)
        self.SetBackgroundColour(self.cp.GetBackgroundColour())
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.cp, flag=wx.EXPAND | wx.ALL, proportion=1, border=3)
        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, e):
        self.Hide()

    def GetTextFromClipboard(self):
        clipboard = wx.Clipboard()
        try:
            if clipboard.Open():
                if clipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                    data = wx.TextDataObject()
                    clipboard.GetData(data)
                    text = data.GetText().strip()
                    if text and text not in self.clip_dict.keys():
                        self.clip_dict[text] = datetime.today()
                        self.cp.on_search(e=None)
                    clipboard.Close()
        except Exception as e:
            pass

    def MyWndProc (self, hWnd, msg, wParam, lParam):
        if msg == win32con.WM_CHANGECBCHAIN:
            self.OnChangeCBChain (msg, wParam, lParam)
        elif msg == win32con.WM_DRAWCLIPBOARD:
            self.OnDrawClipboard (msg, wParam, lParam)

        # Restore the old WndProc. Notice the use of win32api
        # instead of win32gui here. This is to avoid an error due to
        # not passing a callable object.
        if msg == win32con.WM_DESTROY:
            if self.nextWnd:
               win32clipboard.ChangeClipboardChain(self.hwnd, self.nextWnd)
            else:
               win32clipboard.ChangeClipboardChain(self.hwnd, 0)

            win32api.SetWindowLong (self.hwnd,
                                    win32con.GWL_WNDPROC,
                                    self.oldWndProc)

        # Pass all messages (in this case, yours may be different) on
        # to the original WndProc
        return win32gui.CallWindowProc (self.oldWndProc,
                                        hWnd, msg, wParam, lParam)

    def OnChangeCBChain (self, msg, wParam, lParam):
        if self.nextWnd == wParam:
           # repair the chain
           self.nextWnd = lParam
        if self.nextWnd:
           # pass the message to the next window in chain
           win32api.SendMessage (self.nextWnd, msg, wParam, lParam)

    def OnDrawClipboard(self, msg, wParam, lParam):
        if self.first:
            self.first = False
        else:
            self.GetTextFromClipboard()
        if self.nextWnd:
            # pass the message to the next window in chain
            win32api.SendMessage(self.nextWnd, msg, wParam, lParam)


class ClipPanel(wx.Panel):
    def __init__(self, parent, frame, source):
        super().__init__(parent=parent)
        self.frame = frame
        self.source = source
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_edit = wx.SearchCtrl(parent=self, style=wx.WANTS_CHARS)
        self.h_sizer.Add(wx.StaticText(parent=self, label="Search: "),
                         flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT,
                         border=2)
        self.h_sizer.Add(self.search_edit, flag=wx.ALIGN_CENTER_VERTICAL)
        self.list_ctrl = ClipList(self, frame=frame, source=source)

        self.main_sizer.Add(self.h_sizer, flag=wx.LEFT, border=5)
        self.main_sizer.Add(self.list_ctrl, flag=wx.EXPAND | wx.ALL, proportion=1, border=2)
        self.SetSizerAndFit(self.main_sizer)

        self.search_edit.Bind(wx.EVT_TEXT, self.on_search)
        self.search_edit.Bind(wx.EVT_CHAR, self.on_key_down)

    def on_search(self, e):
        self.list_ctrl.filter_list(self.search_edit.GetValue())

    def on_key_down(self, e):
        if e.GetKeyCode() in [wx.WXK_UP, wx.WXK_DOWN]:
            self.list_ctrl.SetFocus()
        e.Skip()


class ClipList(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent, frame, source):
        super().__init__(parent=parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER)
        ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(0)
        self.source = source
        self.filtered_dict: Dict[str, datetime] = {}
        # self.setResizeColumn(0)
        # self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION))
        self.frame = frame
        self.AppendColumn("Text")
        self.AppendColumn("Time")
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION))
        self.SetImageList(self.frame.im_list, wx.IMAGE_LIST_SMALL)
        self.filter_list(filter="")

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)

    def on_item_activated(self, e):
        row = self.GetFirstSelected()
        if row >= 0:
            text = self.GetItemText(row, 0)
            print(text)
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(text))
                wx.TheClipboard.Close()

    def filter_list(self, filter: str) -> None:

        if filter == "":
            self.filtered_dict = self.source
        else:
            self.filtered_dict = {k: v for k, v in self.source.items() if filter.lower() in k.lower()}
        self.DeleteAllItems()
        for k, v in sorted(self.filtered_dict.items(), key=lambda item: item[1], reverse=True):
            row = self.Append([k, v.strftime("%H:%M:%S")])
            self.SetItemImage(row, self.frame.img_clip)


if __name__ == '__main__':
    app = wx.App()
    f = ClipFrame(None)
    f.Show()
    app.MainLoop()
