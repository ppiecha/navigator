import sys
import wx
import wx.lib.agw.customtreectrl as CT
import wx.html as html
import search_const as cn
from pathlib import Path
import re
import wx.dataview
from lib4py import shell as sh
from pubsub import pub
from threading import Thread


def find_words_in_line(text, opt):
    flags = re.IGNORECASE if not opt.case_sensitive else 0
    matches = {}
    for word in opt.words:
        matches[word] = []
        for match in re.finditer(pattern=word, string=text, flags=flags):
            matches[word].append(match.span())
    return matches


class SearchTree(CT.CustomTreeCtrl):
    def __init__(self, parent, frame):
        super().__init__(parent=parent, agwStyle=wx.TR_DEFAULT_STYLE |
                                                 wx.TR_HAS_VARIABLE_ROW_HEIGHT |
                                                 wx.TR_FULL_ROW_HIGHLIGHT |
                                                 wx.TR_HIDE_ROOT)
        self.frame = frame
        self.file_nodes = []
        self.dir_nodes = []
        self.search_nodes = {}
        self.extension_images = {}
        # self.SetHilightFocusColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
        # self.SetHilightNonFocusColour(self.GetBackgroundColour())
        self.EnableSelectionVista()
        # self.SetBorderPen(self.GetConnectionPen())
        # self.SetSeparatorColour(self.GetConnectionPen().GetColour())
        # self.SetDoubleBuffered(True)

        # Image list
        self.il = wx.ImageList(16, 16)
        self.im_search = self.il.Add(wx.Bitmap(cn.CN_IM_NEW_SEARCH, wx.BITMAP_TYPE_PNG))
        self.im_folder = self.il.Add(wx.Bitmap(cn.CN_IM_NEW_FOLDER, wx.BITMAP_TYPE_PNG))
        self.im_file = self.il.Add(wx.Bitmap(cn.CN_IM_NEW_FILE, wx.BITMAP_TYPE_PNG))
        self.im_doc = self.il.Add(wx.Bitmap(cn.CN_IM_NEW_DOC, wx.BITMAP_TYPE_PNG))
        self.AssignImageList(self.il)

        # self.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.on_select)
        # self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.on_tooltip)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.on_collapse)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_expand)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_db_click)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_right_click)

        self.register_topic(cn.CN_TOPIC_ADD_NODE)
        self.register_topic(cn.CN_TOPIC_UPDATE_STATUS)
        self.register_topic(cn.CN_TOPIC_SEARCH_COMPLETED)

    def register_topic(self, topic):
        if topic == cn.CN_TOPIC_ADD_NODE:
            if not pub.subscribe(self.listen_for_nodes, topic):
                raise Exception("Cannot register {topic}")
        elif topic == cn.CN_TOPIC_UPDATE_STATUS:
            if not pub.subscribe(self.listen_for_status, topic):
                raise Exception("Cannot register {topic}")
        elif topic == cn.CN_TOPIC_SEARCH_COMPLETED:
            if not pub.subscribe(self.listen_for_end, topic):
                raise Exception("Cannot register {topic}")

    def listen_for_status(self, status):
        wx.CallAfter(self.frame.SetStatusText, status, 0)

    def listen_for_nodes(self, search_dir, nodes):
        wx.CallAfter(self.add_nodes, search_dir, nodes)

    def run_safe(self, search_dir, node):
        wx.CallAfter(self.search_ended, search_dir, node)

    def run_in_thread(self, target, args):
        th = Thread(target=target, args=args, daemon=True)
        th.start()
        return th

    def listen_for_end(self, search_dir, node):
        self.run_in_thread(self.run_safe, [search_dir, node])

    def search_ended(self, search_dir, node):
        f_cnt = len(self.file_nodes)
        d_cnt = len(self.dir_nodes)
        if f_cnt + d_cnt > 0:
            search_node = self.search_nodes[search_dir]
            if f_cnt == 0:
                stat = f" {d_cnt} folder(s)"
            elif d_cnt == 0:
                stat = f" {f_cnt} file(s)"
            else:
                stat = f" {d_cnt} folders and {f_cnt} files"
            self.update_node_text(search_node, search_node.GetText() + stat)
        else:
            self.add_nodes(search_dir, [node])

    def get_image_id(self, extension):
        """Get the id in the image list for the extension.
        Will add the image if not there already"""
        # Caching
        if extension in self.extension_images:
            return self.extension_images[extension]
        bmp = sh.extension_to_bitmap(extension)
        index = self.il.Add(bmp)
        self.SetImageList(self.il)
        self.extension_images[extension] = index
        return index

    def on_db_click(self, e):
        print("activated")
        e.Skip()

    def on_right_click(self, e):
        item = e.GetItem()
        data = item.GetData()
        if isinstance(data, FileNode):
            path = Path(data.file_full_name)
            sh.get_context_menu(str(path.parent), [path.name])
        elif isinstance(data, DirNode):
            sh.get_context_menu(data.dir, [])
        e.Skip()

    def on_collapse(self, e):
        item = e.GetItem()
        data = item.GetData()
        if isinstance(data, FileNode):
            for child in item.GetChildren():
                win = child.GetWindow()
                if win:
                    win.Hide()
        e.Skip()

    def on_expand(self, e):
        e.Skip()

    def on_sel_changed(self, e):
        e.Skip()

    def on_tooltip(self, e):
        data = e.GetItem().GetData()
        if isinstance(data, FileNode):
            e.SetToolTip(data.file_full_name)
        elif isinstance(data, DirNode):
            e.SetToolTip(data.dir)

    def clear_list(self):
        self.DeleteAllItems()
        self.file_nodes.clear()
        self.dir_nodes.clear()
        self.search_nodes.clear()

    def collapse_all(self):
        for node in self.file_nodes:
            self.Collapse(node)

    def init_tree(self, params=None):
        self.clear_list()
        self.AddRoot("root")
        wx.Yield()


    def update_node_text(self, node, text):
        self.SetItemText(node, text)

    def find_dir_node(self, dir):
        for node in self.dir_nodes:
            if node.GetData().dir == dir:
                return node
        return self.add_dir_node(DirNode(dir=dir))

    def add_search_node(self, search_node):
        item = self.AppendItem(parentId=self.GetRootItem(), text=f"Search result in {Path(search_node.path).name}",
                               data=search_node)
        item.SetBold(True)
        self.search_nodes[search_node.path] = item

    def add_final_node(self, search_node, node):
        item = self.AppendItem(parentId=search_node, text=node.text)
        item.SetBold(True)
        if not self.IsExpanded(search_node):
            self.Expand(search_node)

    def add_nodes(self, search_dir, nodes):
        if nodes:
            if search_dir in self.search_nodes.keys():
                search_node = self.search_nodes[search_dir]
                if isinstance(nodes[0], DirNode):
                    [self.add_dir_node(search_node, d) for d in nodes]
                elif isinstance(nodes[0], FileNode):
                    [self.add_file_node(search_node, f) for f in nodes]
                elif isinstance(nodes[0], FinalNode):
                    self.add_final_node(search_node=search_node, node=nodes[0])
            else:
                raise Exception(f"Cannot find search node for {search_dir}")
        else:
            self.add_search_node(search_node=SearchNode(path=search_dir))
        self.Update()
        # wx.Yield()
        wx.GetApp().ProcessPendingEvents()

    def add_dir_node(self, search_node, dir_node):
        path = Path(dir_node.dir)
        path_dir = str(path.parent.relative_to(Path(search_node.GetData().path)))
        path_dir = path_dir if path_dir != "." else path.parent.name
        item = self.AppendItem(parentId=search_node, text=path.name)
        item.SetWindow(SearchLabel(self, path_dir))
        item.SetWindowEnabled(False)
        item.SetData(dir_node)
        self.SetItemImage(item, self.im_folder)
        self.dir_nodes.append(item)
        return item

    def add_file_node(self, search_node, file_node):

        def add_gui_nodes(lines):
            path = Path(file_node.file_full_name)
            file_dir = str(path.parent.relative_to(Path(search_node.GetData().path)))
            file_dir = file_dir if file_dir != "." else path.parent.name
            file_suffix = path.suffix if path.suffix else '$%#'
            item = self.AppendItem(parentId=search_node, text="", image=self.get_image_id(file_suffix), data=file_node)
            item.SetWindow(SearchLabel(self, file_dir))
            item.SetWindowEnabled(False)
            self.file_nodes.append(item)
            matches_count = 0
            for index, line in enumerate(lines):
                child, matches = self.add_line_node(parent_node=item,
                                                    line_num=line.line_num,
                                                    line_text=line.line_text,
                                                    opt=file_node.opt)
                # item.Insert(child=child, index=index)
                matches_count += matches
            if matches_count == 1:
                item.SetText(text="{0} {1} match".format(path.name, str(matches_count)))
            elif matches_count > 1:
                item.SetText(text="{0} {1} matches".format(path.name, str(matches_count)))
            else:
                item.SetText(text=path.name)
            if not self.IsExpanded(search_node):
                self.Expand(search_node)

        add_gui_nodes(file_node.lines)

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
        item = self.AppendItem(parentId=parent_node, text="Line " + line_num + ":", data=parent_node)
        item.SetWindow(HtmlLabel(parent=self, line_item=item, text=html_text))
        item.SetWindowEnabled(False)
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


class DirNode:
    def __init__(self, dir):
        self.dir = dir


class SearchNode:
    def __init__(self, path):
        self.path = path

class FinalNode:
    def __init__(self, text):
        self.text = text

class HtmlLabel(html.HtmlWindow):
    def __init__(self, parent, line_item, text):
        super().__init__(parent=parent, style=html.HW_SCROLLBAR_NEVER)
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

class SearchLabel(wx.TextCtrl):
    def __init__(self, parent, label):
        super().__init__(parent=parent, value=label, size=(parent.GetTextExtent(label).GetWidth() + 10, 23))


