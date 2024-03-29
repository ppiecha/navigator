import os
import stat
import wx
from datetime import datetime
from pathlib import Path


def format_date(timestamp, format="%Y-%m-%d %H:%M"):
    if not timestamp:
        return ""
    d = datetime.fromtimestamp(timestamp)
    return d.strftime(format)


def format_size(size):
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Y', suffix)

    if not size:
        return ""
    return sizeof_fmt(size) if size != "" else ""


def is_hidden(x: Path) -> bool:
    if not x.exists():
        return True
    try:
        attribute = x.stat().st_file_attributes
    except:
        print("Cannot get attr for", str(x))
        return True
    path, fname = os.path.split(str(x))
    ext = x.suffix
    is_temp_file: bool = False
    if ext:
        is_temp_file = ext.startswith(".~")
        if is_temp_file:
            print("temp file", ext)
    return bool(attribute & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM)) or str(fname).startswith(
        ".") or is_temp_file


class FileDataObject(wx.FileDataObject):
    def __init__(self, nav_frame):
        super().__init__()
        self.nav_frame = nav_frame

    def add_file(self, file):
        file = str(file)
        self.AddFile(file=file)
        if Path(file).is_file():
            self.nav_frame.app_conf.hist_update_file(full_path=str(file), callback=self.nav_frame.refresh_lists)
