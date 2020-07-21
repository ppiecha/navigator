import os
import search_tree
from pathlib import Path
import fnmatch
import re
from pubsub import pub
import search_const as cn
from threading import Thread


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
            pub.sendMessage(cn.CN_TOPIC_ADD_NODE, search_dir=dir_item, node=None)
            for root, dirs, files in os.walk(Path(dir_item)):
                if self.event.is_set():
                    return False
                if root not in opt.ex_dirs:
                    self.set_status(root)
                    dirs_sum += len(dirs)
                    files_sum += len(files)
                    dir_lst = [dir for dir in dirs
                               if dir.lower() not in opt.ex_dirs and self.match(dir, opt.dirs_pattern)]
                    file_lst = [file for file in files
                                if self.match(file, opt.masks)
                                and self.match(file, opt.dirs_pattern)]
                    for dir in dir_lst:
                        if not opt.words:
                            dir_node = search_tree.DirNode(dir=os.path.join(root, dir))
                            pub.sendMessage(cn.CN_TOPIC_ADD_NODE, search_dir=dir_item, node=dir_node)
                    for file in file_lst:
                        if opt.words:
                            self.process_file(dir_item=dir_item, full_file_name=os.path.join(root, file), opt=opt)
                        else:
                            file_node = search_tree.FileNode(file_full_name=os.path.join(root, file), opt=opt)
                            pub.sendMessage(cn.CN_TOPIC_ADD_NODE, search_dir=dir_item, node=file_node)
                else:
                    dirs.clear()
                    files.clear()
            final_node = search_tree.FinalNode(text="No data found")
            pub.sendMessage(cn.CN_TOPIC_SEARCH_COMPLETED, search_dir=dir_item, node=final_node)
        self.set_status("Searched " + "{:,}".format(dirs_sum) + " folder(s) " + "{:,}".format(files_sum) + " file(s) ")
        self.event.set()
        return True

    def run(self):
        res = self.do_search()
        if res:
            # wx.CallAfter(self.frame.change_icon, self.event)
            print("SUCESS")
        else:
            self.set_status("Search cancelled")

    def set_status(self, status):
        # pub.sendMessage(cn.CN_TOPIC_UPDATE_STATUS, status=status)
        pass

    def process_file(self, dir_item, full_file_name, opt):
        try:
            with open(full_file_name, 'r') as f:
                file_node = search_tree.FileNode(file_full_name=full_file_name, opt=opt)
                line_num = 0
                for line_text in f:
                    if self.event.is_set():
                        return False
                    line_text = line_text.rstrip("\n")
                    if self.find_first(text=line_text, opt=opt):
                        file_node.add_line(line_num=str(line_num), line_text=line_text)
                    line_num += 1
                if file_node.lines:
                    pub.sendMessage(cn.CN_TOPIC_ADD_NODE, search_dir=dir_item, node=file_node)
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




