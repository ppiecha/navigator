import os
from threading import Thread
import search_tree
from pathlib import Path
import search_const as cn
import re


class Search(Thread):
    def __init__(self, frame, search_params):
        super().__init__()
        self.frame = frame
        self.exit = False
        self.opt = search_params

    def terminate(self):
        self.exit = True

    def run(self):
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

    def process_file(self, full_file_name, opt):
        with open(full_file_name, 'r') as f:
            path = Path(full_file_name)
            if not path.name == "combo.txt":
                return
            file_node = search_tree.FileNode(file_full_name=full_file_name)
            for line_text in f:
                line_text = line_text.rstrip("\n")
                print([word for word in opt.words if len(line_text.partition(word)[1]) > 0])
                # if list(filter(lambda x: line_text != line_text.partition(x)[0], opt.words)):
                #     line_text.partition(opt.words[0])

    def get_regex_pattern(self, words, opt):
        if cn.OPT_WHOLE_WORD in opt.search_opt:
            return [r"\b" + word + r"\b" for word in words]
        else:
            return [words]

    def find_first(self, text, words, opt):
        words = self.get_regex_pattern(words=words, opt=opt)
        flag = re.IGNORECASE if cn.OPT_WHOLE_WORD in opt.search_opt
        for word in words:
            if re.search(pattern=word, string=text, flags=)

    def find_words_in_line(self, text, words, opt):

        raw_search_string = r"\b" + search_string + r"\b"

        match_output = re.search(raw_search_string, input_string)
        ##As noted by @OmPrakesh, if you want to ignore case, uncomment
        ##the next two lines
        # match_output = re.search(raw_search_string, input_string,
        #                         flags=re.IGNORECASE)

        no_match_was_found = (match_output is None)
        if no_match_was_found:
            return False
        else:
            return True


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



