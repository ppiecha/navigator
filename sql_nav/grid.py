import logging

import wx
import cx_Oracle as oracle
import sql_nav.sql_constants as sql_cn
from lib4py import logger as lg

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)


class SQLGridPnl(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)

        self.tb = wx.ToolBar(parent=self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        self.tb.SetToolBitmapSize((16, 16))
        self.tb.AddTool(toolId=wx.Window.NewControlId(),
                        label="Save",
                        bitmap=wx.Bitmap(sql_cn.IM_SAVE, wx.BITMAP_TYPE_PNG),
                        shortHelp="Save")
        self.tb.Realize()

        self.grid_ctrl: SQLGridCtrl = SQLGridCtrl(parent=self, frame=frame)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tb, flag=wx.EXPAND)
        sizer.Add(self.grid_ctrl, flag=wx.EXPAND, proportion=1)
        self.SetSizer(sizer)


class SQLGridCtrl(wx.ListCtrl):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, style=wx.LC_REPORT | wx.LC_VIRTUAL)
        self.parent = parent
        self.frame = frame
        self.cursor: oracle.Cursor = None

    def load_columns(self, c: oracle.Cursor):
        # columns = [col[0] for col in c.description]
        # c.rowfactory = lambda *args: dict(zip(columns, args))
        if self.cursor:
            self.cursor.close()
        self.cursor = c
        self.DeleteAllItems()
        self.DeleteAllColumns()
        logger.debug("cursor description", c.description)
        for idx, col in enumerate(c.description):
            col_type = col[1]
            logger.debug(type(col[1]))
            if isinstance(col_type, oracle.DB_TYPE_NUMBER):
                prt_format = wx.LIST_FORMAT_RIGHT
            else:
                prt_format = wx.LIST_FORMAT_LEFT
            if self.InsertColumn(col=idx,
                                 heading=col[0],
                                 format=prt_format
                                 ) == -1:
                raise ValueError("Error inserting column: " + str(col))
        logger.debug(str(c.arraysize))
        self.SetItemCount(count=c.arraysize)

    def OnGetItemText(self, item, col):
        logger.debug("OnGetItemText", [item, col])
        self.cursor.scroll(item + 1, mode="absolute")
        row = self.cursor.fetchone()
        return str(row[col])

    def OnGetItemAttr(self, item):
        return None
