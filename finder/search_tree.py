import wx
import wx.lib.agw.customtreectrl as CT
import wx.html as html
import search_const as cn
from pathlib import Path


class SearchTree(CT.CustomTreeCtrl):
    def __init__(self, parent, main_frame):
        super().__init__(parent=parent, agwStyle=wx.TR_DEFAULT_STYLE |
                                                 wx.TR_HAS_VARIABLE_ROW_HEIGHT |
                                                 wx.TR_FULL_ROW_HIGHLIGHT)
        self.root = None
        self.file_nodes = []

        # Image list
        il = wx.ImageList(16, 16)
        self.im_folder = il.Add(wx.Bitmap(cn.CN_IM_NEW_FOLDER, wx.BITMAP_TYPE_PNG))
        self.im_file = il.Add(wx.Bitmap(cn.CN_IM_NEW_FILE, wx.BITMAP_TYPE_PNG))
        self.im_doc = il.Add(wx.Bitmap(cn.CN_IM_NEW_DOC, wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

    def add_root_node(self, root_text):
        self.root = self.AddRoot(root_text)
        self.root.SetBold(True)
        self.root.SetHasPlus(has=False)
        return self.root

    def update_root_node(self, root_text):
        self.SetItemText(self.root, root_text)

    def add_file_node(self, file_node):
        path = Path(file_node.file_full_text)
        item = self.AppendItem(parentId=self.root, text="{0} {1} {2}".format(path.name,
                                                                             str(file_node.matches),
                                                                             str(path)))
        # self.SetItemBold(item)
        self.SetItemImage(item, self.im_file)
        self.file_nodes.append(item)
        for line in file_node.lines:
            self.add_line_node(parent_node=item, line_num=line.line_num, line_text=line.line_text, words=[])
        return item

    def add_line_node(self, parent_node, line_num, line_text, words=[]):
        item = self.AppendItem(parentId=parent_node, text="Line " + line_num + ":")
        # self.SetItemBold(item)
        self.SetItemImage(item, self.im_doc)
        win = HtmlLabel(parent=self, line_item=item, text=line_text, words=words)
        self.SetItemWindow(item, win)
        return item


class LineNode:
    def __init__(self, file_node, line_num, line_text, matches):
        self.file_node = file_node
        self.line_num = line_num
        self.line_text = line_text
        self.matches = matches


class FileNode:
    def __init__(self, file_full_name):
        self.file_full_name = file_full_name
        self.matches = 0
        self.lines = []

    def add_line(self, line_num, line_text, matches):
        line_node = LineNode(file_node=self, line_num=line_num, line_text=line_text, matches=matches)
        self.lines.append(line_node)
        self.matches += matches




class HtmlLabel(html.HtmlWindow):
    def __init__(self, parent, line_item, text, words):
        super().__init__(parent=parent, style=wx.NO_FULL_REPAINT_ON_RESIZE | html.HW_SCROLLBAR_NEVER)
        self.tree = parent
        self.line_item = line_item
        self.font = parent.GetFont()
        self.line_text = ""
        self.template = ""
        self.init()
        self.set_value(text)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)

    def on_left_down(self, e):
        self.tree.SelectItem(item=self.line_item, select=True)
        # self.SelectAll()
        e.Skip()


    def init(self):
        self.SetDefaultHTMLCursor(html.HtmlWindowInterface.HTMLCursor_Text, wx.Cursor(wx.CURSOR_ARROW))
        self.template = '''<html><body text="#000000" bgcolor=":bgcolor">:text</body></html>'''
        self.template = self.template.replace(":bgcolor",
                                              self.tree.GetBackgroundColour().GetAsString(wx.C2S_HTML_SYNTAX))
        font = self.font
        self.SetStandardFonts(font.GetPointSize(), font.GetFaceName(), font.GetFaceName())
        self.SetBorders(0)

    def set_value(self, value):
        self.line_text = self.template.replace(":text", value)
        self.SetPage(source=self.line_text)
        dc = wx.WindowDC(self.tree)
        width, height = dc.GetTextExtent(self.ToText())
        # print(self.ToText(), width)
        self.SetSize(width, height)


