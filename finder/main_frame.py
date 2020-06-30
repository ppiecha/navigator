import wx
import res_frame


class SearchParams:
    def __init__(self, words=[], dirs=[], ex_dirs=[], masks=[], case_sensitive=False, whole_words=False,
                 reg_exp=False, not_contains=False, sub_folders=True):
        self.words = words
        self.dirs = dirs
        self.ex_dirs = ex_dirs
        self.masks = masks
        self.case_sensitive = case_sensitive
        self.whole_words = whole_words
        self.reg_exp = reg_exp
        self.not_contains = not_contains
        self.sub_folders = sub_folders

        self.get_regex_pattern(self.words)

    @staticmethod
    def get_lst(values):
        return [value.strip() for value in values.split(";") if value]

    def get_regex_pattern(self, words):
        if self.whole_words:
            return [r"\b" + word + r"\b" for word in words]
        else:
            return [words]


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Finder", size=(395, 400), style=wx.DEFAULT_DIALOG_STYLE)
        self.main_panel = MainPanel(parent=self, frame=self)

        # self.SetMinSize(self.GetEffectiveMinSize())
        self.Center()


class MainPanel(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.frame = frame
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.options_sizer = wx.GridBagSizer(5, 5)
        self.options_box_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Options")
        self.dir_box_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Directory search")
        self.dir_sizer = wx.GridBagSizer(5, 5)
        self.dlg_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.search_text = wx.ComboBox(self, value="combo")
        self.search_sizer.Add(wx.StaticText(self, label="&Text to find"), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                              border=5)
        self.search_sizer.Add(self.search_text, flag=wx.EXPAND, proportion=1)

        self.case_sensitive = wx.CheckBox(self, label="Case sensitive")
        self.whole_word = wx.CheckBox(self, label="Whole word")
        self.reg_ex = wx.CheckBox(self, label="Regular expresion")
        self.not_contain = wx.CheckBox(self, label="Not contains")
        self.options_sizer.Add(self.case_sensitive, pos=(0, 0), border=3)
        self.options_sizer.Add(self.whole_word, pos=(1, 0), border=3)
        self.options_sizer.Add(self.reg_ex, pos=(2, 0), border=3)
        self.options_sizer.Add(self.not_contain, pos=(0, 1), border=3)

        self.options_box_sizer.Add(self.options_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.directories = wx.ComboBox(self, value=r'c:\Users\pit\Downloads\wxPython-demo-4.1.0\demo')
        self.btn_dir = wx.Button(self, label="...", size=(23, 23))
        self.exclude = wx.ComboBox(self)
        self.mask = wx.ComboBox(self, value="*.py")
        self.sub_dirs = wx.CheckBox(self, label="Search subdirectories")
        self.file_names = wx.CheckBox(self, label="Search also in folder and file names")
        dir_bord = 0
        # Dirs
        self.dir_sizer.Add(wx.StaticText(self, label="Directories"), pos=(0, 0), border=dir_bord,
                           flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.dir_sizer.Add(self.directories, pos=(0, 1), border=dir_bord, span=(0, 10), flag=wx.EXPAND)
        self.dir_sizer.Add(self.btn_dir, pos=(0, 11), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        # Exclude
        self.dir_sizer.Add(wx.StaticText(self, label="Exclude dirs"), pos=(1, 0), border=dir_bord,
                           flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.dir_sizer.Add(self.exclude, pos=(1, 1), border=dir_bord, span=(0, 12), flag=wx.EXPAND)
        # Mask
        self.dir_sizer.Add(wx.StaticText(self, label="File masks"), pos=(2, 0), border=dir_bord,
                           flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        self.dir_sizer.Add(self.mask, pos=(2, 1), border=dir_bord, span=(0, 12), flag=wx.EXPAND)
        # Subdirs
        self.dir_sizer.Add(self.sub_dirs, pos=(3, 1), border=dir_bord, span=(0, 10), flag=wx.EXPAND)
        # File names
        self.dir_sizer.Add(self.file_names, pos=(4, 1), border=dir_bord, span=(0, 10), flag=wx.EXPAND)

        self.dir_box_sizer.Add(self.dir_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # Dialog buttons
        self.btn_search = wx.Button(self, id=wx.ID_OK, label="Search")
        self.btn_search.SetDefault()
        self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="Close")

        self.dlg_sizer.Add(wx.Panel(self), flag=wx.EXPAND, proportion=1)
        self.dlg_sizer.Add(self.btn_search, flag=wx.LEFT, border=5)
        self.dlg_sizer.Add(self.btn_cancel, flag=wx.LEFT, border=5)

        self.main_sizer.Add(self.search_sizer, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)
        self.main_sizer.Add(self.options_box_sizer, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)
        self.main_sizer.Add(self.dir_box_sizer, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)
        self.main_sizer.Add(self.dlg_sizer, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)

        self.SetSizerAndFit(self.main_sizer)

        self.btn_dir.Bind(wx.EVT_BUTTON, self.on_add_dir)
        self.btn_search.Bind(wx.EVT_BUTTON, self.on_search)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_close)

    def get_params(self):
        params = SearchParams(words=SearchParams.get_lst(self.search_text.GetValue()),
                              dirs=SearchParams.get_lst(self.directories.GetValue()),
                              )
        return params

    def on_close(self, e):
        self.frame.Close()

    def on_search(self, e):
        search_result = res_frame.MainFrame(self.frame, self.get_params())
        self.frame.Iconize()
        search_result.Show()
        search_result.SetFocus()

    def on_add_dir(self, e):
        dlg = wx.DirDialog(None, "Select directory", "",
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            if self.directories.GetValue() != "":
                self.directories.SetValue(self.directories.GetValue() + "; " + dlg.GetPath())
            else:
                self.directories.SetValue(dlg.GetPath())
        del dlg

