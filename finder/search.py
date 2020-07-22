import os
import search_tree
from pathlib import Path
import fnmatch
import re
from pubsub import pub
import search_const as cn
import threading
from concurrent import futures


class Search(threading.Thread):
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
        loop_cnt = 0
        dirs_sum = 0
        files_sum = 0
        for dir_item in opt.dirs:
            pub.sendMessage(cn.CN_TOPIC_ADD_NODE, search_dir=dir_item, nodes=None)
            for root, dirs, files in os.walk(Path(dir_item)):
                if self.event.is_set():
                    return False
                if root not in opt.ex_dirs:
                    if loop_cnt % 100 == 0:
                        self.set_status(root)
                    loop_cnt += 1
                    dirs_sum += len(dirs)
                    files_sum += len(files)
                    # DIRS
                    if not opt.words:
                        dir_lst = [dir for dir in dirs
                                   if dir.lower() not in opt.ex_dirs and self.match(dir, opt.dirs_pattern)]
                        if dir_lst:
                            dir_nodes = [search_tree.DirNode(dir=os.path.join(root, d)) for d in dir_lst]
                            pub.sendMessage(cn.CN_TOPIC_ADD_NODE, search_dir=dir_item, nodes=dir_nodes)
                    # FILES
                    file_lst = [os.path.join(root, file) for file in files
                                if self.match(file, opt.masks)
                                and self.match(file, opt.dirs_pattern)]
                    file_nodes = []
                    if opt.words:
                        with futures.ThreadPoolExecutor(max_workers=10) as ex:
                            results = ex.map(lambda x: self.process_file(x, opt, self.event), file_lst)
                            file_nodes = [n for n in results if n is not None]
                    else:
                        if file_lst:
                            file_nodes = [search_tree.FileNode(file_full_name=f, opt=opt)
                                          for f in file_lst]
                    if file_nodes:
                        pub.sendMessage(cn.CN_TOPIC_ADD_NODE, search_dir=dir_item, nodes=file_nodes)
                else:
                    dirs.clear()
                    files.clear()
            final_node = search_tree.FinalNode(text="No data found")
            pub.sendMessage(cn.CN_TOPIC_SEARCH_COMPLETED, search_dir=dir_item, node=final_node)
        self.set_status("Searched " + "{:,}".format(dirs_sum) + " folder(s) " + "{:,}".format(files_sum) + " file(s) ")
        self.event.set()
        return True

    def run(self):
        if not self.do_search():
            self.set_status("Search cancelled")

    def set_status(self, status):
        pub.sendMessage(cn.CN_TOPIC_UPDATE_STATUS, status=status)

    def process_file(self, full_file_name, opt, event):
        try:
            with open(full_file_name, 'r') as f:
                file_node = search_tree.FileNode(file_full_name=full_file_name, opt=opt)
                line_num = 0
                for line_text in f:
                    if event.is_set():
                        return False
                    line_text = line_text.rstrip("\n")
                    if self.find_first(text=line_text, opt=opt):
                        file_node.add_line(line_num=str(line_num), line_text=line_text)
                    line_num += 1
                return file_node if file_node.lines else None
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




