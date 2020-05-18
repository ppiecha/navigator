import os
from threading import Thread
import res_frame
from pathlib import Path


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
                    self.process_file(os.path.join(root, file))
        self.set_status("Searched " + str(dirs_sum) + " folders " + str(files_sum) + " files ")

    def set_status(self, text):
        self.frame.SetStatusText(text, 0)

    def process_file(self, full_file_name):
        # try:
            with open(full_file_name, 'r') as f:
                # print(Path(full_file_name).suffix)
                if not Path(full_file_name).suffix == ".py":
                    return
                file_output = res_frame.ResultItem(full_file_name=full_file_name)
                matches_count = 0
                line_number = 0
                for line_text in f:
                    line_number += 1
                    for word in self.opt.words:
                        if word in line_text:
                            matches_count +=1
                            file_output.add_line(line_number=line_number, line_text=line_text.lstrip())
                if matches_count > 0:
                    file_output.matches_count = matches_count
                    self.frame.output.output.add_file_output(file_output=file_output)
        # except:
        #     print("Error", full_file_name)



