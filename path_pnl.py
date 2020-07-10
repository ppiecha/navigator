import wx
import os
import constants as cn
from pathlib import Path
import dir_label
import links
import dialogs
import controls
from lib4py import shell as sh


class PathPanel(wx.Panel):
    def __init__(self, parent, frame, is_left):
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame
        self.is_left = is_left
        self.tool_dlg = None
        self._read_only = True
        self.drive_combo = self.get_drive_combo()
        self.path_lbl = dir_label.DirLabel(self, self.frame)
        self.path_edit = PathEdit(self, self.frame)
        self.edit_btn = controls.PathBtn(self, frame, cn.CN_IM_OK)
        self.path_edit.Show(False)
        self.edit_btn.Show(False)
        self.edit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.edit_sizer.Add(self.path_edit, flag=wx.EXPAND, proportion=1)
        self.edit_sizer.Add(self.edit_btn)
        self.sep = wx.Panel(self)
        self.links_btn = controls.PathBtn(self, frame, cn.CN_IM_FAV)
        self.hist_btn = controls.PathBtn(self, frame, cn.CN_IM_HIST)
        self.hist_menu = HistMenu()
        self.sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.sizer_h.Add(self.drive_combo)
        self.sizer_h.Add(self.sep, flag=wx.EXPAND, proportion=1)
        self.sizer_h.Add(self.links_btn)
        self.sizer_h.Add(self.hist_btn)
        self.sizer_v.Add(self.path_lbl, flag=wx.EXPAND, proportion=1)
        self.sizer_v.Add(self.edit_sizer, flag=wx.EXPAND, proportion=1)
        self.sizer_v.Add(self.sizer_h, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(self.sizer_v)

        self.hist_btn.Bind(wx.EVT_BUTTON, self.on_history)
        self.links_btn.Bind(wx.EVT_BUTTON, self.on_links)
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_ok)

        wx.CallAfter(self.set_read_only, True)

    def get_drive_combo(self):
        drive_combo = wx.ComboCtrl(self, id=wx.ID_ANY, value="", size=(46, 23), style=wx.CB_READONLY)
        popup_ctrl = ListCtrlComboPopup(path_pnl=self)

        drive_combo.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.on_close_combo)

        # It is important to call SetPopupControl() as soon as possible
        drive_combo.SetPopupControl(popup_ctrl)

        return drive_combo

    def on_close_combo(self, e):
        self.frame.return_focus()

    def on_ok(self, e):
        resp = self.path_edit.exec_path()
        if resp:
            self.read_only = True

    def set_read_only(self, value):
        self.read_only = value

    def set_value(self, value):
        self.path_lbl.set_value(value)
        self.path_edit.SetValue(value)

    @property
    def read_only(self):
        return self._read_only

    @read_only.setter
    def read_only(self, value):
        self.path_lbl.Show(value)
        self.path_edit.Show(not value)
        self.edit_btn.Show(not value)
        if self.path_edit.IsShown():
            self.path_edit.SetFocus()
            self.path_edit.SetInsertionPointEnd()
        self.Layout()
        self._read_only = value

    def AcceptsFocusFromKeyboard(self):
        return False

    def on_links(self, e):
        if not self.tool_dlg:
            self.tool_dlg = links.LinkDlg(self.frame, is_left=self.is_left,
                                          is_read_only=False if wx.GetKeyState(wx.WXK_CONTROL) else True)
        self.tool_dlg.show()
        self.tool_dlg.SetFocus()

    def on_history(self, event):
        self.hist_menu.update()
        self.frame.PopupMenu(self.hist_menu)


class PathEdit(wx.TextCtrl):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.frame = frame
        self.AutoCompleteDirectories()
        self.Bind(wx.EVT_KEY_DOWN, self.on_enter)

    def exec_path(self):
        path = Path(self.GetValue())
        if path.exists():
            if path.is_dir():
                if not path.samefile(Path(self.get_current_dir())):
                    self.open_dir(path)
                    if not str(path).endswith(os.path.sep):
                        self.SetValue(str(path) + os.path.sep)
            else:
                sh.start_file(path)
        else:
            # args = self.GetValue().split()
            # args = [a.trim() for a in args]
            # subprocess.Popen(args, shell=False)
            # result = subprocess.Popen(args, shell=True)
            result = wx.Execute(self.GetValue())
            # if not result:
            #     self.frame.show_message("Cannot execute command")
            # output, error = result.communicate()
            # print(output, error)
        self.SelectNone()
        wx.CallAfter(self.SetInsertionPointEnd)
        return True

    def on_enter(self, e):
        e.Skip()
        if e.GetKeyCode() == wx.WXK_RETURN:
            self.exec_path()

    def open_dir(self, dir):
        self.parent.parent.browser.open_dir(dir_name=dir, sel_dir=cn.CN_GO_BACK)

    def open_file(self, file_name):
        sh.start_file(file_name)

    def context_menu(self, path, item_names):
        sh.get_context_menu(path, item_names)

    def get_current_dir(self):
        if hasattr(self.parent.parent, 'browser'):
            return str(self.parent.parent.browser.path)
        else:
            return ""

    # def on_menu(self, event):
    #     # self.SelectAll()
    #     menu = PathMenu(self.frame, self)
    #     self.frame.PopupMenu(menu)
    #     del menu

    # def on_left_down(self, event):
    #     if self.read_only and self.GetStringSelection():
    #         end = self.get_current_dir().find(self.GetStringSelection()) + len(self.GetStringSelection())
    #         self.open_dir(self.get_current_dir()[:end+1])
    #     event.Skip()

    # def on_kill_focus(self, event):
    #     self.read_only = True
    #     event.Skip()

    # def on_mouse_move(self, event):
    #
    #     def get_text_to_select(parts, pos):
    #         counter = 0
    #         for id, part in enumerate(parts):
    #             counter += len(part) + 1
    #             if counter > pos:
    #                 return parts[id]
    #
    #     if self.read_only and not wx.GetMouseState().LeftIsDown():
    #         x, y = event.GetPosition()
    #         path = self.GetValue()
    #         row, col = self.HitTestPos((x, y))
    #         parts = path.split(os.path.sep)
    #         selection = get_text_to_select(parts, col)
    #         start = path.find(selection)
    #         if start > -1 and not path.endswith(selection) and selection.find("...") == -1:
    #             self.SetFocus()
    #             self.SetSelection(start, start + len(selection))
    #         else:
    #             self.SelectNone()
    #
    #     event.Skip()


    # @property
    # def read_only(self):
    #     return self._read_only
    #
    # @read_only.setter
    # def read_only(self, value):
    #     self.SetEditable(not value)
    #     if value:
    #         self.HideNativeCaret()
    #         self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
    #         self.Bind(wx.EVT_CONTEXT_MENU, self.on_menu)
    #         if self.get_current_dir():
    #             self.SetValue(self.get_shortcut(self.get_current_dir()))
    #         self.SelectNone()
    #     else:
    #         self.ShowNativeCaret()
    #         self.SetCursor(wx.Cursor(wx.CURSOR_IBEAM))
    #         res = self.Unbind(wx.EVT_CONTEXT_MENU)
    #         print(res)
    #         self.SelectAll()
    #     self._read_only = value


class HistMenu(wx.Menu):
    def __init__(self):
        super().__init__()
        self.browser = None
        self.sorted_items = []
        self.sorted_items_id = {}
        self.win = wx.PopupTransientWindow


    def set_browser(self, browser):
        self.browser = browser

    def update(self):
        for item in self.GetMenuItems():
            self.Delete(item)
        self.sorted_items = sorted(self.browser.history)
        self.sorted_items_id = {}
        for item in self.sorted_items:
            self.sorted_items_id[wx.NewId()] = item
        for id in self.sorted_items_id.keys():
            self.Append(id, item=self.sorted_items_id[id])
            self.Bind(wx.EVT_MENU, self.on_click, id=id)

    def on_click(self, event):
        operation = self.sorted_items_id[event.GetId()]
        self.browser.open_dir(operation)

CN_CONFIGURE = "Configure..."


class ListCtrlComboPopup(wx.ComboPopup):
    def __init__(self, path_pnl):
        super().__init__()
        self.path_pnl = path_pnl
        self.frame = path_pnl.frame
        self.lc = None
        self.lc_drives = None
        self.lc_cols = None
        self.item = -1

    def OnMotion(self, evt):
        item, flags = self.lc.HitTest(evt.GetPosition())
        if item >= 0:
            self.lc.Select(item)
            self.item = item
        else:
            self.item = -1
            self.clear_selection()

    def clear_selection(self):
        for idx in range(self.lc.GetItemCount()):
            self.lc.Select(idx, 0)
        self.item = -1

    def OnLeftDown(self, evt):
        if self.item > -1:
            if self.lc.GetItemText(self.item) == CN_CONFIGURE:
                self.Dismiss()
                with dialogs.OptionsDlg(frame=self.frame, title="Options") as dlg:
                    if dlg.show_modal() == wx.ID_OK:
                        self.frame.app_conf.custom_paths = dlg.path_tab.save_cust_paths()
            else:
                self.Dismiss()
                self.path_pnl.path_lbl.open_dir(dir=self.get_sel_path(self.item))

    # The following methods are those that are overridable from the
    # ComboPopup base class.  Most of them are not required, but all
    # are shown here for demonstration purposes.

    # This is called immediately after construction finishes.  You can
    # use self.GetCombo if needed to get to the ComboCtrl instance.
    def Init(self):
        self.item = -1
        self.lc_drives = sh.get_drives()
        self.lc_cols = ["Path", "Name", "Type", "Full Path"]

    # Create the popup child control.  Return true for success.
    def Create(self, parent):
        self.lc = wx.ListCtrl(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER)
        self.lc.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTINACTIVECAPTION))
        for index, name in enumerate(self.lc_cols):
            self.lc.InsertColumn(index, name)
        self.lc.SetImageList(self.frame.im_list, wx.IMAGE_LIST_SMALL)
        # self.lc.EnableAlternateRowColours(True)
        # self.lc.SetAlternateRowColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRADIENTACTIVECAPTION))
        self.prepare_list()
        self.lc.Bind(wx.EVT_MOTION, self.OnMotion)
        self.lc.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        return True

    def prepare_list(self):
        self.lc.DeleteAllItems()
        for drive in self.lc_drives.keys():
            idx = self.lc.Append(self.lc_drives[drive])
            if self.lc_drives[drive][0] == "Desktop":
                self.lc.SetItemImage(idx, self.frame.img_anchor)
            elif self.lc_drives[drive][0] == "Home":
                self.lc.SetItemImage(idx, self.frame.img_home)
            else:
                self.lc.SetItemImage(idx, self.frame.img_hard_disk)

        for name, path in self.frame.app_conf.custom_paths:
            idx = self.lc.Append([name, "", path, path])
            self.lc.SetItemImage(idx, self.frame.img_user)
            self.lc.SetItemTextColour(idx, wx.Colour(0, 0, 64))

        idx = self.lc.Append([CN_CONFIGURE, "", "", ""])
        self.lc.SetItemImage(idx, self.frame.img_tools)

        for index, name in enumerate(self.lc_cols):
            if index < 2:
                self.lc.SetColumnWidth(index, wx.LIST_AUTOSIZE)
            self.lc.SetColumnWidth(3, 0)
            self.lc.SetColumnWidth(2,
                                   self.lc.GetSize().GetWidth() -
                                   self.lc.GetColumnWidth(0) -
                                   self.lc.GetColumnWidth(1))

    # Return the widget that is to be used for the popup
    def GetControl(self):
        return self.lc

    # Called just prior to displaying the popup, you can use it to
    # 'select' the current item.
    def SetStringValue(self, val):
        idx = self.lc.FindItem(-1, val)
        if idx != wx.NOT_FOUND:
            self.lc.Select(idx)

    # Return a string representation of the current item.
    def GetStringValue(self):
        if self.item >= 0 and self.lc.GetItemText(self.item) != CN_CONFIGURE:
            return Path(self.get_sel_path(self.item)).anchor
        else:
            return self.GetComboCtrl().GetValue()

    def get_sel_path(self, index):
        return self.lc.GetItemText(index, 3)

    # Called immediately after the popup is shown
    def OnPopup(self):
        self.prepare_list()
        wx.ComboPopup.OnPopup(self)

    # Called when popup is dismissed
    def OnDismiss(self):
        wx.ComboPopup.OnDismiss(self)

    # This is called to custom paint in the combo control itself
    # (ie. not the popup).  Default implementation draws value as
    # string.
    def PaintComboControl(self, dc, rect):
        wx.ComboPopup.PaintComboControl(self, dc, rect)

    # Receives key events from the parent ComboCtrl.  Events not
    # handled should be skipped, as usual.
    def OnComboKeyEvent(self, event):
        wx.ComboPopup.OnComboKeyEvent(self, event)

    # Implement if you need to support special action when user
    # double-clicks on the parent wxComboCtrl.
    def OnComboDoubleClick(self):
        wx.ComboPopup.OnComboDoubleClick(self)

    # Return final size of popup. Called on every popup, just prior to OnPopup.
    # minWidth = preferred minimum width for window
    # prefHeight = preferred height. Only applies if > 0,
    # maxHeight = max height for window, as limited by screen size
    #   and should only be rounded down, if necessary.
    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        # return wx.ComboPopup.GetAdjustedSize(self, minWidth, prefHeight, maxHeight)
        return self.lc.GetMinSize()

    # Return true if you want delay the call to Create until the popup
    # is shown for the first time. It is more efficient, but note that
    # it is often more convenient to have the control created
    # immediately.
    # Default returns false.
    def LazyCreate(self):
        return wx.ComboPopup.LazyCreate(self)

    def AcceptsFocus(self):
        return False



