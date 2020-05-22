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
    def __init__(self, parent, frame):
        super().__init__(parent=parent, style=pg.PG_TOOLBAR | pg.PGMAN_DEFAULT_STYLE)
        self.parent = parent
        self.frame = frame
        self.SetForegroundColour(wx.BLUE)
        self.SetBackgroundColour(wx.BLACK)
        self.pg_files = self.AddPage("Found in files", wx.Bitmap(cn.CN_IM_FILES, wx.BITMAP_TYPE_PNG))
        self.pg_dirs = self.AddPage("Found in folder and file names", wx.Bitmap(cn.CN_IM_FOLDERS, wx.BITMAP_TYPE_PNG))
        self.SetSplitterPosition(0, 0)
        # self.GetGrid().SetCaptionBackgroundColour(parent.GetBackgroundColour())
        self.GetGrid().SetCaptionTextColour(wx.BLACK)
        self.GetGrid().SetCaptionBackgroundColour(wx.Colour(192, 192, 192))

        self.Bind(pg.EVT_PG_COL_BEGIN_DRAG, self.on_resize)

    def on_resize(self, e):
        print("resize")
        e.Veto()

    def add_file_output(self, file_output):
        file = Path(file_output.full_file_name)
        cat = self.add_category_section(file.name, str(file), file_output.matches_count)
        self.frame.Freeze()
        for line in file_output.lines:
            prop = self.add_line_item(full_file_name=file_output.full_file_name, line_number=line.line_number,
                                      line_text=line.line_text)
            self.Collapse(cat.GetLabel())
            self.pg_files.LimitPropertyEditing(prop.GetLabel(), True)
        self.frame.Thaw()

    def add_category_section(self, file_name, full_file_name, matches_count):
        prop = CategoryProperty(label=file_name, full_file_name=full_file_name, matches_count=matches_count)
        self.pg_files.Append(prop)
        return prop

    def add_line_item(self, full_file_name, line_number, line_text):
        prop = LineProperty(full_file_name=full_file_name, line_number=line_number, text=line_text)
        self.pg_files.Append(prop)
        # self.GetGrid().SelectProperty(prop.GetLabel(), focus=True)
        # ed = self.GetGrid().GetEditorTextCtrl()
        # ed.SetSelection(1, 5)
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


class CategoryProperty(pg.PropertyCategory):
    def __init__(self, label, full_file_name, matches_count):
        super().__init__(label=label + " - " + str(matches_count) + " matches")
        self.full_file_name = full_file_name


class LineProperty(pg.LongStringProperty):
    def __init__(self, full_file_name, line_number, text):
        # super().__init__(label=str(line_number), value=text)
        self.full_file_name = full_file_name
        space = "".join(" " for i in range(100))
        super().__init__(label=str(line_number) + space + str(hash(full_file_name + text)), value=text)

    def OnEvent(self, propgrid, wnd_primary, event):
        # print("on event")
        # print(type(event))
        if event.GetEventType() == wx.EVT_BUTTON:
            print("button")
        #event.Skip()
        return False # wx.propgrid.PGTextCtrlEditor.OnEvent(propgrid, wnd_primary, event)

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
        self.output = Results(parent=self, frame=self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.output, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(sizer)