import logging
from typing import List, Tuple, Any, Optional
from pathlib import Path
import wx
import wx.stc
import sql_nav.sql_constants as sql_cn

from lib4py import logger as lg
from sql_nav.out_editor import SQLOutCtrl, SQLOutPnl
from sql_nav.sql_engine import SQLEng
from sql_nav.sql_util import CmdList, prepare_cmd, SQL_KEYWORDS, is_line_empty, Splitter

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)

faces = {'times': 'Times',
         'mono': 'Consolas',
         'helv': 'Helvetica',
         'other': 'new century schoolbook',
         'size': 9,
         'size2': 9,
         }


class SQLEditor(wx.Panel):
    def __init__(self, parent: wx.Window, frame: wx.Window, file: str = ""):
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame

        self.splitter = Splitter(parent=self)
        self.splitter.SetMinimumPaneSize(10)

        self.sql_edit_pnl = SQLEditPnl(parent=self.splitter, frame=frame, file=file)

        self.out_pnl = SQLOutPnl(parent=self.splitter, frame=frame)
        self.sql_eng = SQLEng(sql_out=self.out_pnl.out_nb.out_ctrl,
                              sql_grid=self.out_pnl.out_nb.out_grid_pnl.grid_ctrl)
        self.sql_eng.start_sql_plus()
        self.sql_eng.connection_str = "hr/oracle@localhost/orcl"
        self.sql_eng.connect_sql_plus()
        self.sql_eng.connect_grid()

        self.splitter.SplitHorizontally(self.sql_edit_pnl, self.out_pnl)
        self.splitter.SetSashGravity(0.5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)


class SQLEditPnl(wx.Panel):
    def __init__(self, parent, frame, file: str = ""):
        super().__init__(parent=parent)
        self.parent = parent
        self.frame = frame

        self.file_path: Optional[Path] = Path(file) if file else None

        self.tb = wx.ToolBar(parent=self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        self.tb.SetToolBitmapSize((16, 16))
        self.tb.AddTool(toolId=wx.Window.NewControlId(),
                        label="Save",
                        bitmap=wx.Bitmap(sql_cn.IM_SAVE, wx.BITMAP_TYPE_PNG),
                        shortHelp="Save")
        self.tb.Realize()

        self.sql_edit = SQLEditCtrl(parent=self, file=file)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tb, flag=wx.EXPAND)
        sizer.Add(self.sql_edit, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)

    def get_caption(self, tab_num: int) -> str:
        logger.debug("file path "+str(self.file_path))
        if self.file_path and self.file_path.exists():
            return self.file_path.name
        else:
            return "sql" + str(tab_num + 1)


class SQLEditCtrl(wx.stc.StyledTextCtrl):
    def __init__(self, parent: wx.Window, file: str):
        wx.stc.StyledTextCtrl.__init__(self, parent, -1, style=wx.BORDER_NONE)
        self.setup_editor()
        if file:
            self.open_file(file_name=file)

    def setup_editor(self):
        self.SetLexer(wx.stc.STC_LEX_SQL)
        self.SetKeyWords(0, ' '.join(SQL_KEYWORDS))
        self.SetProperty('fold', '3')
        self.SetProperty('tab.timmy.whinge.level', '1')
        self.SetMargins(2, 2)
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 40)
        self.SetIndent(4)
        self.SetIndentationGuides(True)
        self.SetBackSpaceUnIndents(True)
        self.SetTabIndents(True)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.SetViewWhiteSpace(False)
        self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetViewEOL(False)
        self.SetEdgeMode(wx.stc.STC_EDGE_NONE)
        self.SetMarginType(2, wx.stc.STC_MARGIN_COLOUR)
        self.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        # STC_MARGIN_BACK = 2
        # STC_MARGIN_COLOUR = 6
        # STC_MARGIN_FORE = 3
        # STC_MARGIN_NUMBER = 1
        # STC_MARGIN_RTEXT = 5
        # STC_MARGIN_SYMBOL = 0
        # STC_MARGIN_TEXT = 4

        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "fore:#404040,back:#E0E0E0,face:%(mono)s,size:%(size2)d" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")

        try:
            self.StyleSetSpec(wx.stc.STC_SQL_COMMENT, "fore:#7F7F7F,size:%(size)d" % faces)
            self.StyleSetSpec(wx.stc.STC_SQL_COMMENTLINE, "fore:#007F00,face:%(mono)s,size:%(size)d" % faces)
            self.StyleSetSpec(wx.stc.STC_SQL_WORD, "fore:#00007F,size:%(size)d" % faces)
        except:
            self.StyleSetSpec(1, "fore:#7F7F7F,size:%(size)d" % faces)
            self.StyleSetSpec(5, "fore:#00007F,bold,size:%(size)d" % faces)

        """STC_SQL_CHARACTER
        STC_SQL_COMMENT
        STC_SQL_COMMENTDOC
        STC_SQL_COMMENTDOCKEYWORD
        STC_SQL_COMMENTDOCKEYWORDERROR
        STC_SQL_COMMENTLINE
        STC_SQL_COMMENTLINEDOC
        STC_SQL_DEFAULT
        STC_SQL_IDENTIFIER
        STC_SQL_NUMBER
        STC_SQL_OPERATOR
        STC_SQL_QUOTEDIDENTIFIER
        STC_SQL_SQLPLUS
        STC_SQL_SQLPLUS_COMMENT
        STC_SQL_SQLPLUS_PROMPT
        STC_SQL_STRING
        STC_SQL_USER1
        STC_SQL_USER2
        STC_SQL_USER3
        STC_SQL_USER4
        STC_SQL_WORD
        STC_SQL_WORD2"""

    def ShowPosition(self, pos):
        line = self.LineFromPosition(pos)
        # self.EnsureVisible(line)
        self.GotoLine(line)

    def GetRange(self, start, end):
        return self.GetTextRange(start, end)

    def GetLastPosition(self):
        return self.GetLength()

    def open_file(self, file_name: str) -> None:
        self.LoadFile(filename=file_name)

    def get_last_not_empty(self, act_line: int):
        if act_line == self.GetLineCount() - 1:
            """Last line"""
            return act_line
        else:
            for line in range(act_line, self.GetLineCount()):
                if is_line_empty(line_str=self.GetLine(line)):
                    return line - 1
            return self.GetLineCount()

    def get_first_not_empty(self, act_line: int):
        if act_line == 0:
            """First line"""
            return 0
        else:
            for line in range(act_line - 1, -1, -1):
                if is_line_empty(line_str=self.GetLine(line)):
                    return line + 1
            return 0

    def is_comment(self, pos: int) -> bool:
        if self.GetStyleAt(pos) in (wx.stc.STC_SQL_COMMENT, wx.stc.STC_SQL_COMMENTLINE):
            return True
        else:
            return False

    def get_cmd_list(self) -> CmdList:
        cmd_list = []
        line = self.GetCurrentLine()
        line_str = self.GetLine(line)
        if is_line_empty(line_str=line_str) or self.is_comment(self.GetCurrentPos()):
            pass
        else:
            cmd_str: str
            if self.GetSelectedText():
                cmd_str = self.GetSelectedText()
            else:
                cmd_str = self.GetRange(start=self.PositionFromLine(self.get_first_not_empty(act_line=line)),
                                        end=self.GetLineEndPosition(self.get_last_not_empty(act_line=line)))

            # logger.debug(cmd)
            cmd = prepare_cmd(cmd_str=cmd_str)
            logger.debug(cmd.cmd)
            if cmd:
                cmd_list.append(cmd)
        return cmd_list
