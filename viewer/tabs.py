import wx
import editor
import wx.aui as aui
from pathlib import Path


class EditorPanel(wx.Panel):
    def __init__(self, parent, frame, file_name, read_only=False):
        super().__init__(parent=parent)
        self.frame = frame

        self.editor = editor.Editor(parent=self, file_name=file_name, read_only=read_only)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.editor, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(sizer)


class EditorBook(aui.AuiNotebook):
    def __init__(self, frame):
        super().__init__(parent=frame, style=aui.AUI_NB_TAB_MOVE | aui.AUI_NB_TAB_SPLIT |
                                             aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_TOP)
        # self.SetArtProvider(aui.AuiDefaultTabArt())
        self.frame = frame

    def add_tab(self, file_name=None, read_only=False, select=False):
        self.Freeze()
        tab = EditorPanel(parent=self, frame=self.frame, file_name=file_name, read_only=read_only)
        tab_name = Path(file_name).stem if file_name else "Untitled"
        self.AddPage(page=tab, caption=tab_name, select=select)
        self.Thaw()

    # def add_new_tab(self, dir_name):
    #     tab_conf = config.BrowserConf()
    #     tab_conf.last_path = dir_name if dir_name else Path.home()
    #     self.conf.append(tab_conf)
    #     self.add_tab(tab_conf=tab_conf, select=True)