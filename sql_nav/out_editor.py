import wx
import wx.stc
import wx.aui as aui
import sql_nav.sql_constants as sql_cn

from sql_nav.grid import SQLGridPnl

faces = {'times': 'Times',
         'mono': 'Consolas',
         'helv': 'Helvetica',
         'other': 'new century schoolbook',
         'size': 8,
         'size2': 8,
         }


def is_error(text: str) -> bool:
    return text.startswith("ERROR") or \
           text.startswith("ORA-") or \
           text.startswith("SP2-") or \
           text.startswith("PLS-")


def add_end_of_line(text: str) -> str:
    if not text.endswith("\n"):
        return text + "\n"
    else:
        return text


class SQLOutPageCtrl(aui.AuiNotebook):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, style=aui.AUI_NB_TOP)
        self.parent = parent
        self.frame = frame

        self.out_ctrl = SQLOutCtrl(parent=self)
        self.AddPage(page=self.out_ctrl,
                     caption="Output",
                     select=True)
        self.out_grid_pnl: SQLGridPnl = SQLGridPnl(parent=self, frame=frame)
        self.AddPage(page=self.out_grid_pnl,
                     caption="Grid",
                     select=False)


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

        self.out_nb = SQLOutPageCtrl(parent=self, frame=frame)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tb, flag=wx.EXPAND)
        sizer.Add(self.out_nb, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)


class SQLOutCtrl(wx.stc.StyledTextCtrl):
    def __init__(self, parent):
        wx.stc.StyledTextCtrl.__init__(self, parent, -1, style=wx.BORDER_NONE)
        self.setup_editor()

    def print_error(self, error: str) -> None:
        self.append("ERROR: " + error + "\n")

    def append(self, text: str) -> None:
        start = self.GetLength()
        text = add_end_of_line(text=text)
        self.SetEditable(editable=True)
        self.AppendText(text=text)
        self.SetEditable(editable=False)
        end = self.GetLength()
        if is_error(text=text):
            self.set_styling(start=start, end=end, style_spec=wx.stc.STC_STYLE_MAX)
        else:
            self.set_styling(start=start, end=end, style_spec=wx.stc.STC_STYLE_DEFAULT)
        self.GotoLine(self.LineFromPosition(self.GetLength()))

    def set_styling(self, start: int, end: int, style_spec: int) -> None:
        self.StartStyling(start=start)
        self.SetStyling(end - start, style_spec)
        # self.StartStyling(start=end)
        # self.SetStyling(0, wx.stc.STC_STYLE_DEFAULT)

    def setup_editor(self):
        self.SetProperty('fold', '1')
        self.SetProperty('tab.timmy.whinge.level', '1')
        self.SetMargins(2, 2)
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 40)
        # self.SetIndent(4)
        # self.SetIndentationGuides(True)
        # self.SetBackSpaceUnIndents(True)
        # self.SetTabIndents(True)
        # self.SetTabWidth(4)
        self.SetUseTabs(True)
        self.SetViewWhiteSpace(False)
        self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetViewEOL(False)
        self.SetEdgeMode(wx.stc.STC_EDGE_NONE)
        self.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)

        self.StyleClearAll()  # Reset all to be like the default

        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, "fore:#808080,back:#E0E0E0,face:%(mono)s,size:%(size2)d" % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_MAX, "fore:#FF0000,face:%(mono)s,size:%(size)d" % faces)

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
        STC_SQL_WORD"""