from typing import List

import wx
import wx.stc
import constants as cn
import sql_nav.sql_constants as sql_cn
import logging
from lib4py import logger as lg
from sql_nav.out_editor import SQLOutCtrl
from sql_nav.sql_editor import SQLEditCtrl, SQLEditor
from sql_nav.sql_engine import SQLEng
import wx.aui as aui
from pathlib import Path

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
        page = SQLPnl(parent=self, frame=self, path=path, files=files)
        self.dir_nb.AddPage(page=page, caption=page.get_caption(path=path), select=True)
        self.set_caption(caption=page.get_caption(path=path))
        return True

    def set_caption(self, caption: str) -> None:
        pass

    def is_duplicate(self, path: str) -> bool:
        return False

    def on_exec(self, e):
        if self.dir_nb.get_act_page().sql_eng:
            self.dir_nb.get_act_page().sql_eng.exec_in_sql_plus(cmd_list=self.dir_nb.get_act_page().edit_pnl.sql_edit.get_cmd_list(),
                                                                edit_mode=e.GetId())
        else:
            raise ValueError("SQLPlus process not active")

    def on_close(self, e):
        e.Veto()
        if self.nav_frame.get_question_feedback("Are you sure you want to close SQL editor? ") == wx.ID_YES:
            self.Hide()
            for idx in range(self.dir_nb.GetPageCount()):
                self.dir_nb.GetPage(page_idx=idx).sql_eng.close()





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
                page.sql_edit.SetFocus()
            elif isinstance(page, SQLPnl):
                act_page = page.edit_pnl.file_nb.get_act_page()
                if act_page:
                    act_page.sql_edit.SetFocus()

    def get_act_page(self):
        selection = self.GetSelection()
        logger.debug("selection" + str(selection))
        if selection >= 0:
            return self.GetPage(page_idx=selection)
        else:
            return None

    # def AcceptsFocus(self):
    #     return False
    #
    # def CanAcceptFocus(self):
    #     return False
    #
    # def AcceptsFocusFromKeyboard(self):
    #     return False


class SQLEditPnl(wx.Panel):
    def __init__(self, parent: wx.Window, frame: wx.Window, files=None):
        super().__init__(parent=parent)
        self.files = files
        self.parent = parent
        self.frame = frame

        self.file_nb = SQLPageCtrl(parent=self)

        if files:
            for file in files:
                self.add_page(file=str(file))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.file_nb, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.sizer)

    def add_page(self, file: str) -> bool:
        if self.is_duplicate(path=file):
            return True
        page = SQLEditor(parent=self, frame=self, file=file)
        self.file_nb.AddPage(page=page, caption=page.get_caption(tab_num=self.file_nb.GetPageCount()), select=True)
        # self.set_caption(caption=page.get_caption(path=path))
        return True

    def is_duplicate(self, path: str) -> bool:
        return False


class SQLOutPnl(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame

        self.tb = wx.ToolBar(parent=self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        self.tb.SetToolBitmapSize((16, 16))
        self.tb.AddTool(toolId=wx.Window.NewControlId(),
                        label="Save",
                        bitmap=wx.Bitmap(sql_cn.IM_SAVE, wx.BITMAP_TYPE_PNG),
                        shortHelp="Save")
        self.tb.Realize()

        self.sql_out = SQLOutCtrl(parent=self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tb, flag=wx.EXPAND)
        sizer.Add(self.sql_out, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)


class SQLPnl(wx.Panel):
    def __init__(self, parent: wx.Window, frame: wx.Window, path: str, files=None) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame
        self.path: str = path
        self.files = files

        self.splitter_main = wx.SplitterWindow(self, cn.ID_SQL_SPLITTER1, style=wx.SP_BORDER)
        self.splitter_main.SetMinimumPaneSize(10)
        self.splitter_right = wx.SplitterWindow(self.splitter_main, cn.ID_SQL_SPLITTER2, style=wx.SP_BORDER)
        self.splitter_right.SetMinimumPaneSize(10)

        self.tree = wx.GenericDirCtrl(self.splitter_main,
                                      size=(200, 225),
                                      style=wx.DIRCTRL_SHOW_FILTERS | wx.DIRCTRL_3D_INTERNAL,
                                      filter="SQL files (*.sql;*.pks;*.pkb)|*.sql;*.pks;*.pkb|All files (*.*)|*.*")
        self.tree.ExpandPath(path=str(path))

        self.edit_pnl = SQLEditPnl(parent=self.splitter_right,
                                   frame=frame,
                                   files=files)
        self.out_pnl = SQLOutPnl(parent=self.splitter_right, frame=frame)
        self.sql_eng = SQLEng(sql_out=self.out_pnl.sql_out)
        self.sql_eng.start_sql_plus()
        self.sql_eng.connection_str = "hr/oracle@localhost/orcl"
        self.sql_eng.connect_sql_plus()

        self.splitter_main.SplitVertically(self.tree, self.splitter_right)
        self.splitter_right.SplitHorizontally(self.edit_pnl, self.out_pnl)
        self.splitter_right.SetSashGravity(0.5)

        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer_main.Add(self.splitter_main, proportion=1, flag=wx.EXPAND)

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

