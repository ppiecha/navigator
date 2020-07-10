import wx
import search_const as cn
import sys


class MainFrame(wx.Frame):
    def __init__(self, app):
        super().__init__(parent=None, title=cn.CN_APP_NAME, size=(400, 375), style=wx.DEFAULT_DIALOG_STYLE)
        self.app = app
        self.res_frame = None
        self.main_panel = MainPanel(parent=self, frame=self)
        self.app.SetAppDisplayName(cn.CN_APP_NAME)
        self.app.SetAppName(cn.CN_APP_NAME)
        self.SetIcon(wx.Icon(cn.CN_ICON_FILE_NAME))
        self.SetMinSize(self.GetEffectiveMinSize())
        self.Center()

        self.process_args()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, e):
        self.res_frame.Destroy()
        self.Destroy()

    def process_args(self):
        if len(sys.argv) > 1:
            opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
            args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
            self.main_panel.directories.SetValue(args[0])
            self.main_panel.search_text.Clear()
        else:
            pass


class MainPanel(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.frame = frame
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.search_text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_dir_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_sizer = wx.BoxSizer(wx.VERTICAL)
        self.options_sizer = wx.GridBagSizer(5, 5)
        self.options_box_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Options")
        self.dir_box_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Directory search")
        self.dir_sizer = wx.GridBagSizer(5, 5)
        self.dlg_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.search_text = wx.ComboBox(self, value="combo")
        self.search_text_sizer.Add(wx.StaticText(self, label="Text to find"), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                                   border=5)
        self.search_text_sizer.Add(self.search_text, flag=wx.EXPAND, proportion=1)

        self.search_dir = wx.ComboBox(self, value="")
        self.search_dir_sizer.Add(wx.StaticText(self, label="File/folder  "), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                                  border=5)
        self.search_dir_sizer.Add(self.search_dir, flag=wx.EXPAND, proportion=1)

        self.search_sizer.Add(self.search_text_sizer, flag=wx.EXPAND)
        self.search_sizer.Add(self.search_dir_sizer, flag=wx.EXPAND | wx.TOP, border=5)

        self.case_sensitive = wx.CheckBox(self, label="Case sensitive")
        self.whole_word = wx.CheckBox(self, label="Whole word")
        self.reg_ex = wx.CheckBox(self, label="Regular expresion")
        self.not_contain = wx.CheckBox(self, label="Not contains")
        self.sub_dirs = wx.CheckBox(self, label="Subdirs")

        self.options_sizer.Add(self.case_sensitive, pos=(0, 0), border=3)
        self.options_sizer.Add(self.whole_word, pos=(1, 0), border=3)
        self.options_sizer.Add(self.reg_ex, pos=(2, 0), border=3)
        self.options_sizer.Add(self.not_contain, pos=(0, 1), border=3)
        self.options_sizer.Add(self.sub_dirs, pos=(1, 1), border=3)

        self.options_box_sizer.Add(self.options_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.directories = wx.ComboBox(self, value=r'c:\Users\pit')
        self.btn_dir = wx.Button(self, label="...", size=(23, 23))
        self.exclude = wx.ComboBox(self, value="")
        self.mask = wx.ComboBox(self, value="*.sql;*.pkb;*.pks;*.py")
        # self.sub_dirs = wx.CheckBox(self, label="Search subdirectories")
        # self.file_names = wx.CheckBox(self, label="Search also in folder and file names")
        dir_bord = 0
        # Dirs
        self.dir_sizer.Add(wx.StaticText(self, label="Directories"), pos=(0, 0), border=dir_bord,
                           flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.dir_sizer.Add(self.directories, pos=(0, 1), border=dir_bord, span=(0, 17), flag=wx.EXPAND)
        self.dir_sizer.Add(self.btn_dir, pos=(0, 18), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        # Exclude
        self.dir_sizer.Add(wx.StaticText(self, label="Exclude dirs"), pos=(1, 0), border=dir_bord,
                           flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.dir_sizer.Add(self.exclude, pos=(1, 1), border=dir_bord, span=(0, 18), flag=wx.EXPAND)
        # Mask
        self.dir_sizer.Add(wx.StaticText(self, label="File masks"), pos=(2, 0), border=dir_bord,
                           flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.dir_sizer.Add(self.mask, pos=(2, 1), border=dir_bord, span=(0, 18), flag=wx.EXPAND)
        # Subdirs
        # self.dir_sizer.Add(self.sub_dirs, pos=(3, 1), border=dir_bord, span=(0, 10), flag=wx.EXPAND)
        # File names
        # self.dir_sizer.Add(self.file_names, pos=(4, 1), border=dir_bord, span=(0, 10), flag=wx.EXPAND)

        self.dir_box_sizer.Add(self.dir_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # Dialog buttons
        self.btn_search = wx.Button(self, id=wx.ID_OK, label="Search")
        self.btn_search.SetDefault()
        self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="Close")

        self.dlg_sizer.Add(wx.Panel(self), flag=wx.EXPAND, proportion=1)
        self.dlg_sizer.Add(self.btn_search, flag=wx.RIGHT, border=5)
        self.dlg_sizer.Add(self.btn_cancel, flag=wx.RIGHT , border=15)

        self.main_sizer.Add(self.search_sizer, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)
        self.main_sizer.Add(self.options_box_sizer, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)
        self.main_sizer.Add(self.dir_box_sizer, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)
        self.main_sizer.Add(self.dlg_sizer, flag=wx.TOP | wx.BOTTOM | wx.EXPAND, border=10)

        self.SetSizer(self.main_sizer)

        self.btn_dir.Bind(wx.EVT_BUTTON, self.on_add_dir)
        self.btn_search.Bind(wx.EVT_BUTTON, self.on_search)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_close)

    def get_params(self):
        params = SearchParams(words=SearchParams.get_lst(self.search_text.GetValue()),
                              dirs_pattern=SearchParams.get_lst(self.search_dir.GetValue(), lower=True),
                              dirs=SearchParams.get_lst(self.directories.GetValue()),
                              ex_dirs=SearchParams.get_lst(self.exclude.GetValue(), lower=True),
                              masks=SearchParams.get_lst(self.mask.GetValue(), lower=True),
                              case_sensitive=self.case_sensitive.IsChecked(),
                              whole_words=self.whole_word.IsChecked(),
                              reg_exp=self.reg_ex.IsChecked(),
                              sub_folders=self.sub_dirs.IsChecked()
                              )
        return params

    def on_close(self, e):
        self.frame.Close()

    def on_search(self, e):
        self.frame.res_frame.set_params(self.get_params())
        self.frame.Hide()
        self.frame.res_frame.Show()
        self.frame.res_frame.start_search()
        self.frame.res_frame.SetFocus()

    def on_add_dir(self, e):
        dlg = wx.DirDialog(None, "Select directory", "",
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            if self.directories.GetValue() != "":
                self.directories.SetValue(self.directories.GetValue() + "; " + dlg.GetPath())
            else:
                self.directories.SetValue(dlg.GetPath())
        del dlg


class SearchParams:
    def __init__(self, words=[], dirs_pattern=[], dirs=[], ex_dirs=[], masks=[], case_sensitive=False,
                 whole_words=False, reg_exp=False, not_contains=False, sub_folders=True):
        self.words = words
        self.dirs_pattern = dirs_pattern
        self.dirs = dirs
        self.ex_dirs = ex_dirs
        self.masks = masks
        self.case_sensitive = case_sensitive
        self.whole_words = whole_words
        self.reg_exp = reg_exp
        self.not_contains = not_contains
        self.sub_folders = sub_folders

        self.get_regex_pattern(self.words)
        self.dirs_pattern = self.set_match_pattern(self.dirs_pattern)
        self.masks = self.set_match_pattern(self.masks)

    def __repr__(self):
        return str(self.words) + str(self.dirs_pattern) + str(self.dirs) + str(self.ex_dirs) + str(self.masks)

    @staticmethod
    def get_lst(values, lower=False):
        return [value.lower() if lower else value for value in values.split(";") if value]

    def get_regex_pattern(self, words):
        if self.whole_words:
            return [r"\b" + word + r"\b" for word in words]
        else:
            return [words]

    def set_match_pattern(self, dirs_pattern):
        lst = []
        if dirs_pattern:
            for pat in dirs_pattern:
                lst.append(pat if "*" in pat else "*" + pat + "*")
        else:
            lst.append("*")
        return lst


