import os
from threading import Thread
import search_tree
from pathlib import Path
import search_const as cn
import re
import wx

def run_in_thread(target, args):
    th = Thread(target=target, args=args)
    th.start()
    return th


class Search(Thread):
    def __init__(self, frame, search_params):
        super().__init__()
        self.frame = frame
        self.exit = False
        self.opt = search_params

    def terminate(self):
        self.exit = True

    def run(self):
        tree = self.frame.output.tree
        tree.DeleteAllItems()
        tree.add_root_node("Search results for {0} in {1}".format(self.opt.words,
                                                                  [str(Path(dir)) for dir in self.opt.dirs]))
        tree.SetFocus()
        tree.SelectItem(tree.root)
        tree.add_separator()
        tree.Expand(tree.root)
        dirs_sum = 0
        files_sum = 0
        for dir_item in self.opt.dirs:
            for root, dirs, files in os.walk(dir_item):
                self.set_status(root)
                dirs_sum += len(dirs)
                files_sum += len(files)
                for dir in dirs:
                    if self.exit:
                        return
                for file in files:
                    if self.exit:
                        return
                    self.process_file(os.path.join(root, file), self.opt)
        self.set_status("Searched " + str(dirs_sum) + " folders " + str(files_sum) + " files ")

    def set_status(self, text):
        self.frame.SetStatusText(text, 0)

    def call_after(self, fun, arg):
        wx.CallAfter(fun, arg)

    def process_file(self, full_file_name, opt):
        with open(full_file_name, 'r') as f:
            path = Path(full_file_name)
            if not path.suffix == ".py":
                return
            file_node = search_tree.FileNode(file_full_name=full_file_name, opt=opt)
            line_num = 0
            for line_text in f:
                line_text = line_text.rstrip("\n")
                if self.find_first(text=line_text, opt=opt):
                    file_node.add_line(line_num=str(line_num), line_text=line_text)
                line_num += 1
            if file_node.lines:
                run_in_thread(self.call_after, [self.frame.output.tree.add_file_node, file_node])

    def find_first(self, text, opt):
        for word in opt.words:
            if re.search(pattern=word, string=text, flags=re.IGNORECASE if not opt.case_sensitive else 0):
                return True
        return False

        # try:
        #     with open(full_file_name, 'r') as f:
        #         # print(Path(full_file_name).suffix)
        #         if not Path(full_file_name).suffix == ".py":
        #             return
        #         file_output = res_frame.ResultItem(full_file_name=full_file_name)
        #         matches_count = 0
        #         line_number = 0
        #         for line_text in f:
        #             line_number += 1
        #             for word in self.opt.words:
        #                 if word in line_text:
        #                     matches_count +=1
        #                     file_output.add_line(line_number=line_number, line_text=line_text.lstrip())
        #         if matches_count > 0:
        #             file_output.matches_count = matches_count
        #             self.frame.output.output.add_file_output(file_output=file_output)
        # except:
        #     print("Error", full_file_name)



