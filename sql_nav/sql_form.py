import wx
import wx.stc
from util import constants as cn
import sql_nav.sql_constants as sql_cn
import logging
from lib4py import logger as lg
from sql_nav.sql_editor import SQLEditor
from pathlib import Path
import wx.aui as aui
from sql_nav.sql_util import Splitter

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)

CN_ID_SCRIPT = wx.Window.NewControlId()
CN_ID_EXEC = wx.Window.NewControlId()
CN_ID_EXE_FILE = wx.Window.NewControlId()


class SQLFrame(wx.Frame):
    def __init__(self, nav_frame):
        super().__init__(parent=None, title=cn.CN_SQL_NAVIGATOR, size=(700, 500), style=wx.DEFAULT_FRAME_STYLE)
        self.SetIcon(wx.Icon(sql_cn.IM_DB))
        self.nav_frame = nav_frame
        self.dir_nb = SQLPageCtrl(parent=self)

        self.CenterOnScreen()

        self.entries = []
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_ESCAPE, cmd=wx.ID_CANCEL))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_F5, cmd=CN_ID_SCRIPT))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_CTRL, keyCode=wx.WXK_RETURN, cmd=CN_ID_EXEC))
        self.entries.append(wx.AcceleratorEntry(flags=wx.ACCEL_NORMAL, keyCode=wx.WXK_F9, cmd=CN_ID_EXE_FILE))

        self.SetAcceleratorTable(wx.AcceleratorTable(self.entries))

        self.Bind(wx.EVT_MENU, self.on_exec, id=CN_ID_EXEC)
        # self.Bind(wx.EVT_MENU, self.on_find, id=CN_ID_FIND)
        # self.Bind(wx.EVT_MENU, self.on_copy_selected, id=CN_ID_COPY)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # self.add_page(path=r'C:\Users\piotr\_piotr_\__GIT__\Oracle\scripts')

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.dir_nb, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.sizer)

    def add_page(self, path: str, files=None) -> bool:
        if self.is_duplicate(path=path):
            return True
        page = SQLPnl(parent=self.dir_nb, frame=self, path=path, files=files)
        self.dir_nb.AddPage(page=page, caption=page.get_caption(path=path), select=True)
        self.set_caption(caption=page.get_caption(path=path))
        return True

    def set_caption(self, caption: str) -> None:
        pass

    def is_duplicate(self, path: str) -> bool:
        return False

    def on_exec(self, e):
        act_dir: SQLPnl = self.dir_nb.get_act_page()
        if act_dir:
            act_file: SQLEditor = act_dir.edit_pnl.get_act_page()
            if act_file and act_file.sql_eng:
                cmd_list = act_file.sql_edit_pnl.sql_edit.get_cmd_list()
                act_file.sql_eng.exec_in_sql_plus(cmd_list=cmd_list,
                                                  edit_mode=e.GetId())
                act_file.sql_eng._exec_in_grid(cmd_list=cmd_list,
                                               params=[])

    def on_close(self, e):
        e.Veto()
        if self.nav_frame.get_question_feedback(parent=self,
                                                question="Are you sure you want to close SQL editor? ") == wx.ID_YES:
            self.Hide()
            for idx in range(self.dir_nb.GetPageCount()):
                self.dir_nb.GetPage(page_idx=idx).edit_pnl.close()


class SQLPageCtrl(aui.AuiNotebook):
    def __init__(self, parent):
        super().__init__(parent=parent, style=aui.AUI_NB_CLOSE_ON_ALL_TABS | aui.AUI_NB_SCROLL_BUTTONS |
                                              aui.AUI_NB_TOP | aui.AUI_NB_WINDOWLIST_BUTTON)

        self.Bind(wx.EVT_CHILD_FOCUS, self.on_child_focus)

    def on_child_focus(self, e):
        win = wx.Window.FindFocus()
        if isinstance(win, aui.AuiTabCtrl):
            page = self.get_act_page()
            if isinstance(page, SQLEditor):
                page.sql_edit_pnl.sql_edit.SetFocus()
            elif isinstance(page, SQLPnl):
                act_page = page.edit_pnl.get_act_page()
                if act_page:
                    act_page.sql_edit_pnl.sql_edit.SetFocus()

    def get_act_page(self):
        selection = self.GetSelection()
        if selection >= 0:
            return self.GetPage(page_idx=selection)
        else:
            return None


class SQLFilePnl(SQLPageCtrl):
    def __init__(self, parent: wx.Window, frame: wx.Window, files=None):
        super().__init__(parent=parent)
        self.files = files
        self.parent = parent
        self.frame = frame

        if files:
            for file in files:
                self.add_page(file=str(file))

    def add_page(self, file: str) -> bool:
        if self.is_duplicate(path=file):
            return True
        page = SQLEditor(parent=self, frame=self, file=file)
        self.AddPage(page=page,
                     caption=page.sql_edit_pnl.get_caption(tab_num=self.GetPageCount()),
                     select=True)
        # self.set_caption(caption=page.get_caption(path=path))
        return True

    def close(self):
        for idx in range(self.GetPageCount()):
            self.GetPage(page_idx=idx).sql_eng.close()

    def is_duplicate(self, path: str) -> bool:
        return False


class SQLPnl(wx.Panel):
    def __init__(self, parent: wx.Window, frame: wx.Window, path: str, files=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame
        self.path: str = path
        self.files = files

        self.splitter = Splitter(parent=self)
        self.splitter.SetMinimumPaneSize(10)

        self.tree = wx.GenericDirCtrl(self.splitter,
                                      size=(200, 225),
                                      style=wx.DIRCTRL_SHOW_FILTERS | wx.DIRCTRL_3D_INTERNAL,
                                      filter="SQL files (*.sql;*.pks;*.pkb)|*.sql;*.pks;*.pkb|All files (*.*)|*.*")
        self.tree.ExpandPath(path=str(path))

        self.edit_pnl = SQLFilePnl(parent=self.splitter,
                                   frame=frame,
                                   files=files)

        self.splitter.SplitVertically(self.tree, self.edit_pnl)
        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.splitter, proportion=1, flag=wx.EXPAND)

        # self.Bind(wx.EVT_SIZE, self.on_size)
        # self.Bind(wx.EVT_SPLITTER_DCLICK, self.on_db_click, id=cn.ID_SPLITTER)
        self.tree.Bind(wx.EVT_DIRCTRL_FILEACTIVATED, self.on_db_click)

        self.SetSizerAndFit(self.sizer_main)

    def get_caption(self, path: str) -> str:
        full_path: Path = Path(path)
        if full_path.is_dir():
            return str(full_path.name)
        else:
            return str(full_path.parent.name)

    def on_db_click(self, e):
        if self.tree.GetFilePath():
            self.edit_pnl.add_page(file=self.tree.GetFilePath())


class SQLNavigator(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.frame = SQLFrame(nav_frame=None)
        self.frame.Show()


if __name__ == '__main__':
    app = SQLNavigator()
    app.MainLoop()

