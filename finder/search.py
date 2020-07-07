import os
from threading import Thread
import search_tree
from pathlib import Path
import fnmatch
import re
import wx


def run_in_thread(target, args):
    th = Thread(target=target, args=args, daemon=True)
    th.start()
    return th


class Search(Thread):
    def __init__(self, frame, search_params, event):
        super().__init__()
        self.frame = frame
        self.event = event
        self.opt = search_params
        self.denied_items = []

    def match(self, src, pat_lst):
        return len(list(filter(lambda x: fnmatch.fnmatch(src, x), pat_lst))) > 0

    def do_search(self):
        opt = self.opt
        self.denied_items.clear()
        dirs_sum = 0
        files_sum = 0
        for dir_item in opt.dirs:
            for root, dirs, files in os.walk(dir_item):
                if root not in opt.ex_dirs:
                    self.set_status(root)
                    dir_lst = [dir for dir in dirs
                               if dir.lower() not in opt.ex_dirs and self.match(dir, opt.dirs_pattern)]
                    file_lst = [file for file in files
                                if self.match(file, opt.masks)
                                and self.match(file, opt.dirs_pattern)]
                    dirs_sum += len(dirs)
                    files_sum += len(files)
                    for dir in dir_lst:
                        if not opt.words:
                            dir_node = search_tree.DirNode(dir=os.path.join(root, dir))
                            wx.CallAfter(self.frame.output.tree.add_dir_node, dir_node)
                    for file in file_lst:
                        if opt.words:
                            self.process_file(os.path.join(root, file), opt)
                        else:
                            file_node = search_tree.FileNode(file_full_name=os.path.join(root, file), opt=opt)
                            wx.CallAfter(self.frame.output.tree.add_file_node, file_node)
                        if self.event.is_set():
                            return False

        self.set_status("Searched " + str(dirs_sum) + " folders " + str(files_sum) + " files ")
        self.event.set()
        return True

    def run(self):
        res = self.do_search()
        if res:
            wx.CallAfter(self.frame.change_icon, self.event)
            print("SUCESS")
        else:
            self.set_status("Search cancelled")

    def set_status(self, text):
        if text != self.frame.GetStatusBar().GetStatusText(0):
            wx.CallAfter(self.frame.SetStatusText, text, 0)

    def call_after(self, fun, arg):
        wx.CallAfter(fun, arg)

    def process_file(self, full_file_name, opt):
        # print(full_file_name)
        try:
            with open(full_file_name, 'r') as f:
                path = Path(full_file_name)
                file_node = search_tree.FileNode(file_full_name=full_file_name, opt=opt)
                line_num = 0
                for line_text in f:
                    line_text = line_text.rstrip("\n")
                    if self.find_first(text=line_text, opt=opt):
                        file_node.add_line(line_num=str(line_num), line_text=line_text)
                    line_num += 1
                if file_node.lines:
                    # wx.CallAfter(self.frame.output.tree.add_file_node, file_node)
                    wx.CallAfter(self.frame.output.tree.add_file_node, file_node)
        except UnicodeDecodeError:
            pass
        except PermissionError:
            self.denied_items.append(full_file_name)
        except OSError as e:
            print(str(e))


    def find_first(self, text, opt):
        for word in opt.words:
            if re.search(pattern=word, string=text, flags=re.IGNORECASE if not opt.case_sensitive else 0):
                return True
        return False




