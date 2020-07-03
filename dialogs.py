import wx
import constants as cn
import browser
import os
import wx.html as html
import wx.propgrid as pg
from pathlib import Path
import controls

CN_ID_LOWER = wx.NewId()
CN_ID_UPPER = wx.NewId()

class BasicDlg(wx.Dialog):
    def __init__(self, frame, title, size=(500, 500), style=wx.DEFAULT_DIALOG_STYLE, border=10):
        super().__init__(parent=frame, title=title, size=size if size else wx.DefaultSize, style=style)

        self.entries = []
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_ESCAPE, cmd=wx.ID_CANCEL))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_CTRL, keyCode=ord("L"), cmd=CN_ID_LOWER))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_CTRL, keyCode=ord("U"), cmd=CN_ID_UPPER))

        self.SetAcceleratorTable(wx.AcceleratorTable(self.entries))

        # Sizers
        self.ctrl_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.dlg_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Dialog buttons
        self.static_line = wx.StaticLine(self)
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label="OK")
        self.btn_ok.SetDefault()
        self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="Cancel")

        # Add buttons
        self.dlg_sizer.Add(wx.Panel(self), flag=wx.EXPAND, proportion=1)
        self.dlg_sizer.Add(self.btn_ok, flag=wx.LEFT, border=5)
        self.dlg_sizer.Add(self.btn_cancel, flag=wx.LEFT, border=5)

        self.main_sizer.Add(self.ctrl_sizer, flag=wx.ALL | wx.EXPAND, border=border, proportion=1)
        self.main_sizer.Add(self.static_line, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=border)
        self.main_sizer.Add(self.dlg_sizer, flag=wx.ALL | wx.EXPAND, border=border)

        self.SetSizer(self.main_sizer)

        self.Bind(event=wx.EVT_MENU, handler=self.on_lower, id=CN_ID_LOWER)
        self.Bind(event=wx.EVT_MENU, handler=self.on_upper, id=CN_ID_UPPER)

    @staticmethod
    def change_case(ctrl, upper=True):
        sel = ctrl.GetStringSelection()
        if sel:
            start, stop = ctrl.GetSelection()
            val = ctrl.GetValue()
            begin, mid, end = val[:start], val[start:stop], val[stop:]
            mid = mid.upper() if upper else mid.lower()
            ctrl.ChangeValue(begin + mid + end)
            ctrl.SetSelection(start, stop)
        else:
            ctrl.ChangeValue(ctrl.GetValue().upper() if upper else ctrl.GetValue().lower())


    def on_lower(self, e):
        pass

    def on_upper(self, e):
        pass

    def on_cancel(self, e):
        self.EndModal(wx.ID_CANCEL)
        e.Skip()

    def show_modal(self, fit=True):
        if fit:
            self.main_sizer.Fit(self)
        self.CenterOnParent()
        return self.ShowModal()


CN_CUSTOM_PATHS = "Custom paths"


class PathEditor(pg.PropertyGrid):
    def __init__(self, parent, main_frame, frame):
        super().__init__(parent=parent, style=pg.PGMAN_DEFAULT_STYLE)
        self.parent = parent
        self.frame = frame
        self.main_frame = main_frame
        self.Append(pg.PropertyCategory(label=CN_CUSTOM_PATHS))
        self.load_cust_paths()

    def load_cust_paths(self):
        for name, path in self.main_frame.app_conf.custom_paths:
            self.Append(pg.DirProperty(label=name, value=path))

    def save_cust_paths(self):
        lst = []
        iterator = self.GetPyIterator(pg.PG_ITERATE_ALL)
        for prop in iterator:
            if isinstance(prop, pg.DirProperty):
                lst.append((prop.GetLabel(), prop.GetValue()))
        return lst

    def validate_cust_paths(self):
        iterator = self.GetPyIterator(pg.PG_ITERATE_ALL)
        for prop in iterator:
            if isinstance(prop, pg.DirProperty):
                if not Path(prop.GetValue()).exists():
                    self.SelectProperty(prop, focus=True)
                    wx.MessageBox(message="Incorrect path for: " + prop.GetLabel(), caption=cn.CN_APP_NAME)
                    return False
        return True


class PathTab(wx.Panel):
    def __init__(self, parent, main_frame, frame):
        super().__init__(parent=parent)
        self.frame = frame
        self.main_frame = main_frame

        # Sizers
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        btn_add = controls.PathBtn(self, frame, cn.CN_IM_ADD)
        btn_edit = controls.PathBtn(self, frame, cn.CN_IM_EDIT)
        btn_remove = controls.PathBtn(self, frame, cn.CN_IM_REMOVE)

        btn_sizer.AddMany([btn_add, btn_edit, btn_remove])

        self.path_edt = PathEditor(self, main_frame, frame)

        main_sizer.Add(btn_sizer)
        main_sizer.Add(self.path_edt, flag=wx.EXPAND, proportion=1)

        self.SetSizerAndFit(main_sizer)

        btn_add.Bind(wx.EVT_BUTTON, self.add_path)
        btn_edit.Bind(wx.EVT_BUTTON, self.edit_path)
        btn_remove.Bind(wx.EVT_BUTTON, self.remove_path)

    def add_path(self, e):
        with TextEditDlg(frame=self.frame, title="New custom path",
                         label="Enter new path name", edit_text="") as dlg:
            if dlg.show_modal() == wx.ID_OK:
                for item in dlg.get_new_names():
                    item = self.path_edt.Append(pg.DirProperty(label=item, value=""))
                    (res, value) = item.DisplayEditorDialog(self.path_edt, item.GetValue())
                    if res:
                        item.SetValue(value)

    def edit_path(self, e):
        prop = self.path_edt.GetSelection()
        if prop:
            with TextEditDlg(frame=self.frame, title="Edit custom path",
                             label="Enter new path name", edit_text=prop.GetLabel()) as dlg:
                if dlg.show_modal() == wx.ID_OK:
                    prop.SetLabel(dlg.get_new_names()[0])
        else:
            wx.MessageBox(message="Select path to edit", caption=cn.CN_APP_NAME)

    def remove_path(self, e):
        prop = self.path_edt.GetSelection()
        if prop:
            if self.main_frame.get_question_feedback("Are you sure you want to remove path: " +
                                                     prop.GetLabel()) == wx.YES:
                self.path_edt.DeleteProperty(prop)
        else:
            wx.MessageBox(message="Select path to remove", caption=cn.CN_APP_NAME)

    def save_cust_paths(self):
        return self.path_edt.save_cust_paths()


class OptionsDlg(BasicDlg):
    def __init__(self, frame, title):
        super().__init__(frame=frame, title=title, size=(500, 300))
        self.opt_book = wx.Listbook(self)
        self.path_tab = PathTab(parent=self.opt_book, main_frame = frame, frame=self)
        self.opt_book.AddPage(page=self.path_tab, text=CN_CUSTOM_PATHS, select=True)

        self.opt_book.GetListView().SetColumnWidth(0, wx.LIST_AUTOSIZE)

        self.ctrl_sizer.Add(self.opt_book, flag=wx.ALL | wx.EXPAND, border=5, proportion=1)

        self.btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)

    def on_ok(self, e):
        if self.path_tab.path_edt.validate_cust_paths():
            e.Skip()
        else:
            return

    def show_modal(self):
        self.main_sizer.Fit(self)
        self.SetSize(self.GetEffectiveMinSize())
        self.CenterOnParent()
        self.path_tab.path_edt.SetFocus()
        prop = self.path_tab.path_edt.GetFirst(pg.PG_ITERATE_NORMAL)
        if prop:
            self.path_tab.path_edt.SelectProperty(prop)
        return self.ShowModal()


class HTMLDlg(BasicDlg):
    def __init__(self, frame, title, text, img_id):
        super().__init__(frame=frame, title=title)
        template = '''<html><body text="#000000" bgcolor=":bgcolor">:text</body></html>'''
        bmp = wx.ArtProvider.GetBitmap(img_id, size=(32, 32))
        img = wx.StaticBitmap(self, -1, bmp)
        self.html = html.HtmlWindow(self, style=wx.NO_FULL_REPAINT_ON_RESIZE, size=(400, 80))
        template = template.replace(":bgcolor", self.GetBackgroundColour().GetAsString(wx.C2S_HTML_SYNTAX))
        template = template.replace(":text", text)
        font = self.GetFont()
        self.html.SetStandardFonts(font.GetFractionalPointSize(), font.GetFaceName(), font.GetFaceName())
        self.html.SetPage(source=template)
        int_sizer = wx.BoxSizer(wx.HORIZONTAL)
        int_sizer.Add(img, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        int_sizer.Add(self.html)
        self.ctrl_sizer.Add(int_sizer)


class DeleteDlg(HTMLDlg):
    def __init__(self, frame, text):
        super().__init__(frame=frame, title="Delete", text=text, img_id=wx.ART_WARNING)
        self.cb_perm = wx.CheckBox(parent=self, label="Delete permanently (bypass recycle bin)")
        self.cb_perm.SetValue(wx.CHK_UNCHECKED)
        self.ctrl_sizer.Add(self.cb_perm, flag=wx.TOP, border=5)


class TextEditDlg(BasicDlg):
    def __init__(self, frame, title, label="", edit_text=""):
        super().__init__(frame=frame, title=title)
        self.lbl_text = wx.StaticText(self, label=label)
        self.ed_new_name = controls.FileNameEdit(parent=self, size=(400, 23), value=edit_text)
        self.ctrl_sizer.Add(self.lbl_text)
        self.ctrl_sizer.Add(self.ed_new_name, flag=wx.TOP, border=5)

        self.btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)

    def on_ok(self, e):
        if self.get_new_names():
            e.Skip()
        else:
            self.mb(message="New name is empty")
            self.ed_new_name.SetFocus()
            return

    def mb(self, message):
        wx.MessageBox(message=message, caption=cn.CN_APP_NAME)
        self.ed_new_name.SetFocus()
        self.ed_new_name.SelectAll()
        self.ed_new_name.SetInsertionPointEnd()

    def get_new_names(self):
        items = self.ed_new_name.GetValue().rstrip(";").split(";")
        return [item.rstrip() for item in items]

    def set_focus(self):
        self.ed_new_name.SetFocus()
        self.ed_new_name.SetInsertionPointEnd()

    def select_all(self):
        self.set_focus()
        self.ed_new_name.smart_select()

    def show_modal(self):
        self.main_sizer.Fit(self)
        self.SetSize(self.GetEffectiveMinSize())
        self.CenterOnParent()
        return self.ShowModal()

    def on_lower(self, e):
        BasicDlg.change_case(self.ed_new_name, upper=False)

    def on_upper(self, e):
        BasicDlg.change_case(self.ed_new_name, upper=True)

class NewItemDlg(TextEditDlg):
    def __init__(self, frame, title, browser_path, def_name, label=""):
        super().__init__(frame=frame, title=title)
        self.browser_path = browser_path
        self.ed_new_name.SetValue(def_name)
        self.lbl_text.SetLabel(label)

    def on_ok(self, e):
        new_names = self.get_new_names()
        if new_names:
            for i in new_names:
                parts = i.split(os.path.sep)
                parts = [part.rstrip() for part in parts]
                no_spaces = os.path.sep.join(parts)
                path = self.browser_path.joinpath(no_spaces)
                if path.exists():
                    self.mb(message=str(path) + " exists")
                    return
                else:
                    e.Skip()
        else:
            self.mb(message="New name is empty")
            return

    def show_modal(self):
        self.select_all()
        return super().show_modal()


class NewFolderDlg(NewItemDlg):
    def __init__(self, frame, browser_path, def_name):
        super().__init__(frame=frame, title="Create new folder", browser_path=browser_path, def_name=def_name)
        self.lbl_text.SetLabelText("Enter new folder name")


class LockTabDlg(TextEditDlg):
    def __init__(self, frame, edit_text=None):
        super().__init__(frame=frame,
                         title=browser.CN_LOCK_RENAME,
                         label="Enter new name for the tab",
                         edit_text=edit_text)


class NewFileDlg(NewItemDlg):
    def __init__(self, frame, browser_path, def_name):
        super().__init__(frame=frame, title="Create new text file", browser_path=browser_path, def_name=def_name)
        self.lbl_text.SetLabelText("Enter new file name")
        self.cb_open = wx.CheckBox(parent=self, label="Open created file")
        self.cb_open.SetValue(wx.CHK_UNCHECKED)
        self.ctrl_sizer.Add(self.cb_open, flag=wx.TOP, border=5)


class RenameDlg(TextEditDlg):
    def __init__(self, frame, item_name):
        super().__init__(frame=frame, title="Rename")
        self.frame = frame
        self.lbl_text.SetLabelText("Enter new name for " + item_name)
        self.ed_new_name.SetValue(item_name)
        self.cb_rename = wx.CheckBox(parent=self, label="Rename on collision")
        self.cb_rename.SetValue(wx.CHK_CHECKED)
        self.ctrl_sizer.Add(self.cb_rename, flag=wx.TOP, border=5)

    def show_modal(self):
        self.set_focus()
        self.ed_new_name.smart_select()
        return super().show_modal()


class CopyMoveDlg(BasicDlg):
    def __init__(self, frame, title, opr_count, src, dst, show_cb=True):
        super().__init__(frame=frame, title=title)
        self.lbl_opr_count = wx.StaticText(parent=self, label=opr_count)
        self.lbl_from = wx.StaticText(parent=self, label=src)
        self.ed_dst = controls.FileNameEdit(parent=self, value=str(dst), size=(400, 23))
        self.dir_btn = wx.Button(self, label='...', size=(23, 23))
        self.dir_btn.Bind(wx.EVT_BUTTON, self.on_dir_btn)
        self.dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dir_sizer.Add(self.ed_dst, flag=wx.EXPAND, proportion=1)
        self.dir_sizer.Add(self.dir_btn)
        self.cb_rename = wx.CheckBox(parent=self, label="Rename on collision")
        self.cb_rename.SetValue(wx.CHK_CHECKED)
        self.cb_rename.Show(show_cb)
        self.ctrl_sizer.Add(self.lbl_opr_count)
        self.ctrl_sizer.Add(self.lbl_from)
        self.ctrl_sizer.Add(self.dir_sizer, flag=wx.TOP | wx.EXPAND, border=5, proportion=1)
        self.ctrl_sizer.Add(self.cb_rename, flag=wx.TOP, border=5)

    def on_dir_btn(self, e):
        path, name = self.get_path_and_name()
        dir = wx.DirSelector(message="Select directory", default_path=str(path))
        if dir:
            self.ed_dst.SetValue(dir)

    def mb(self, message):
        wx.MessageBox(message=message, caption=cn.CN_APP_NAME)
        self.ed_dst.SetFocus()
        self.ed_dst.SelectAll()

    def get_path_and_name(self):
        path = Path(self.ed_dst.GetValue())
        if path.suffix:
            return path.parent, path.name
        else:
            return path, ""

    def show_modal(self):
        self.ed_dst.SetFocus()
        self.ed_dst.SetInsertionPointEnd()
        self.ed_dst.smart_select()
        return super().show_modal()

    def on_lower(self, e):
        BasicDlg.change_case(self.ed_dst, upper=False)

    def on_upper(self, e):
        BasicDlg.change_case(self.ed_dst, upper=True)





