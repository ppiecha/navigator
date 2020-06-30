import wx
import wx.lib.agw.customtreectrl as CT
import wx.html as html
import search_const as cn
from pathlib import Path
import re
import wx.dataview


def find_words_in_line(text, opt):
    flags = re.IGNORECASE if not opt.case_sensitive else 0
    matches = {}
    for word in opt.words:
        matches[word] = []
        for match in re.finditer(pattern=word, string=text, flags=flags):
            matches[word].append(match.span())
    return matches


class SearchTree(CT.CustomTreeCtrl):
    def __init__(self, parent, main_frame):
        super().__init__(parent=parent, agwStyle=wx.TR_DEFAULT_STYLE |
                                                 wx.TR_HAS_VARIABLE_ROW_HEIGHT |
                                                 wx.TR_FULL_ROW_HIGHLIGHT)
                                                 # wx.TR_ELLIPSIZE_LONG_ITEMS)
        self.root = None
        self.file_nodes = []
        # self.SetHilightFocusColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
        # self.SetHilightNonFocusColour(self.GetBackgroundColour())
        self.EnableSelectionVista()
        # self.SetBorderPen(self.GetConnectionPen())
        # self.SetSeparatorColour(self.GetConnectionPen().GetColour())
        self.SetDoubleBuffered(True)

        # Image list
        il = wx.ImageList(16, 16)
        self.im_search = il.Add(wx.Bitmap(cn.CN_IM_NEW_SEARCH, wx.BITMAP_TYPE_PNG))
        self.im_folder = il.Add(wx.Bitmap(cn.CN_IM_NEW_FOLDER, wx.BITMAP_TYPE_PNG))
        self.im_file = il.Add(wx.Bitmap(cn.CN_IM_NEW_FILE, wx.BITMAP_TYPE_PNG))
        self.im_doc = il.Add(wx.Bitmap(cn.CN_IM_NEW_DOC, wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        self.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.on_select)

    def on_select(self, e):
        self.SetItemTextColour(e.GetItem(), wx.BLACK)
        print("sel")
        e.Skip()

    def add_root_node(self, root_text):
        self.root = self.AddRoot(root_text)
        self.root.SetBold(True)
        self.SetItemImage(self.root, self.im_search)
        return self.root

    def add_separator(self):
        self.AppendSeparator(self.root)

    def update_node_text(self, node, text):
        self.SetItemText(node, text)

    def add_file_node(self, file_node):
        # self.Freeze()
        matches_count = 0
        path = Path(file_node.file_full_name)
        item = self.AppendItem(parentId=self.root, text="{0} {1} matches".format(path.name,
                                                                                 str(matches_count)))
        self.SetItemBold(item)
        # self.SetItemImage(item, self.im_file)
        self.SetItemImage(item, self.im_doc)
        self.file_nodes.append(item)
        matches_count = 0
        for line in file_node.lines:
            child, matches = self.add_line_node(parent_node=item,
                                                line_num=line.line_num,
                                                line_text=line.line_text,
                                                opt=file_node.opt)
            matches_count += matches
        self.update_node_text(node=item,
                              text="{0} {1} matches".format(path.name,
                                                            str(matches_count)))
        self.add_separator()
        # self.Thaw()
        return item

    def add_line_node(self, parent_node, line_num, line_text, opt):
        matches = find_words_in_line(line_text, opt)
        matches_count = 0
        html_text = line_text
        for word, lst in matches.items():
            matches_count += len(lst)
            cnt = 0
            for s1, s2 in lst:
                start = s1 + cnt * 7
                stop = s2 + cnt * 7
                html_text = html_text[:start] + "<b>" + html_text[start:stop] + "</b>" + html_text[stop:]
                cnt += 1
            # html_text = ("<b>" + word + "</b>").join([part for part in line_text.split(word)])
        item = self.AppendItem(parentId=parent_node, text="Line " + line_num + ":")
        # self.SetItemImage(item, self.im_doc)
        win = HtmlLabel(parent=self, line_item=item, text=html_text)
        self.SetItemWindow(item, win)
        return item, matches_count


class LineNode:
    def __init__(self, file_node, line_num, line_text):
        self.file_node = file_node
        self.line_num = line_num
        self.line_text = line_text


class FileNode:
    def __init__(self, file_full_name, opt):
        self.file_full_name = file_full_name
        self.opt = opt
        self.matches = 0
        self.lines = []

    def add_line(self, line_num, line_text):
        line_node = LineNode(file_node=self, line_num=line_num, line_text=line_text)
        self.lines.append(line_node)


class HtmlLabel(html.HtmlWindow):
    def __init__(self, parent, line_item, text):
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
        self.template = '''<html><body text="#000000" bgcolor=":bgcolor"><p>:text</p></body></html>'''
        self.template = self.template.replace(":bgcolor",
                                              self.tree.GetBackgroundColour().GetAsString(wx.C2S_HTML_SYNTAX))
        font = self.font
        self.SetStandardFonts(font.GetPointSize(), font.GetFaceName(), font.GetFaceName())
        self.SetBorders(0)

    def set_value(self, value):
        self.line_text = self.template.replace(":text", value)
        # print(self.line_text)
        self.SetPage(source=self.line_text)
        dc = wx.WindowDC(self.tree)
        width, height = dc.GetTextExtent(self.ToText())
        self.SetSize(width, height)


