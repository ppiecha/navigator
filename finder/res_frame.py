from pathlib import Path
import wx
import wx.propgrid as pg
import search_const as cn
import search


class MainFrame(wx.MiniFrame):
    def __init__(self, finder, search_params):
        super().__init__(parent=None, title="Search results", size=(395, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.finder = finder
        self.status_bar = self.CreateStatusBar(1)
        self.search_params = search_params
        self.searches = []
        self.output = MainPanel(self, self)
        print(search_params.words)

        self.Center()

        self.Bind(wx.EVT_CLOSE, self.on_close)

        wx.CallAfter(self.start_search, self.search_params)

    def start_search(self, opt):
        s = search.Search(self, opt)
        self.searches.append(s)
        s.start()

    def on_close(self, e):
        self.finder.Close()
        e.Skip()


class Results(pg.PropertyGridManager):
    def __init__(self, parent):
        super().__init__(parent=parent, style=pg.PG_TOOLBAR | pg.PGMAN_DEFAULT_STYLE)
        # self.SetFont(wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))
        self.pg_files = self.AddPage("Found in files", wx.Bitmap(cn.CN_IM_FILES, wx.BITMAP_TYPE_PNG))
        self.SetSplitterPosition(0, 0)
        # page.Append(pg.PropertyCategory("Category A1"))
        # page.Append(pg.StringProperty(label="test1", value="test2"))
        # page.Append(pg.LongStringProperty("LongString",
        #                                   value="This is a\nmulti-line string\nwith\ttabs\nmixed\tin."))
        #
        # page.Append(FileNameProperty("Category B2"))
        # page.Append(pg.StringProperty(label="test2", value="test3"))
        # page.Append(pg.ColourProperty("Colour", pg.PG_LABEL, wx.WHITE))
        self.pg_dirs = self.AddPage("Found in folder and file names", wx.Bitmap(cn.CN_IM_FOLDERS, wx.BITMAP_TYPE_PNG))
        # page.Append(pg.PropertyCategory("Category A1"))
        # page.Append(pg.StringProperty(label="test1", value="test2"))
        # page.Append(pg.LongStringProperty("LongString",
        #                                   value="This is a\nmulti-line string\nwith\ttabs\nmixed\tin."))
        #
        # page.Append(FileNameProperty("Category B2"))
        # page.Append(pg.StringProperty(label="test2", value="test3"))
        # page.Append(pg.ColourProperty("Colour", pg.PG_LABEL, wx.WHITE))

        self.pg_files.Bind(pg.EVT_PG_LABEL_EDIT_BEGIN, self.on_edit)

    def on_edit(self, e):
        print("On edit")
        e.Veto()

    def add_file_output(self, file_output):
        file = Path(file_output.full_file_name)
        cat = self.add_file_section(file.name, str(file), file_output.matches_count)
        for line in file_output.lines:
            self.add_file_item(line_number=line.line_number, line_text=line.line_text)
        self.pg_files.Collapse(cat.GetLabel())

    def add_file_section(self, file_name, full_file_name, matches_count):
        prop = FileNameProperty(label=file_name, full_file_name=full_file_name, matches_count=matches_count)
        self.pg_files.Append(prop)
        return prop

    def add_file_item(self, line_number, line_text):
        prop = LineProperty(line_number=line_number, text=line_text)
        self.pg_files.Append(prop)
        return prop


class Line:
    def __init__(self, line_number, line_text):
        self.line_number = line_number
        self.line_text = line_text


class ResultItem:
    def __init__(self, full_file_name):
        self.full_file_name = full_file_name
        self.matches_count = 0
        self.lines = []

    def add_line(self, line_number, line_text):
        self.lines.append(Line(line_number, line_text))


class FileNameProperty(pg.PropertyCategory):
    def __init__(self, label, full_file_name, matches_count):
        super().__init__(label=label + " - " + str(matches_count) + " matches")
        self.full_file_name = full_file_name


class LineProperty(pg.LongStringProperty):
    def __init__(self, line_number, text):
        # super().__init__(label=str(line_number), value=text)
        super().__init__(label="", value=str(line_number) + " " + text)


    def OnButtonClick(self, propGrid, value):
        dlgSize = wx.Size()
        dlgPos = propGrid.GetGoodEditorDialogPosition(self, dlgSize)

        # Create dialog dlg at dlgPos. Use value as initial string
        # value.
        with MyCustomDialog(None, title, pos=dlgPos, size=dlgSize) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                value = dlg.GetStringValue()
                return (True, value)
            return (False, value)


class MainPanel(wx.Panel):
    def __init__(self, parent, frame):
        super().__init__(parent=parent)
        self.frame = frame
        self.output = Results(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.output, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(sizer)