from datetime import datetime
from win32com.shell import shell, shellcon
from win32con import FILE_ATTRIBUTE_NORMAL
import wx
import stat
import os
import win32api


def get_drives():
    drives = win32api.GetLogicalDriveStrings()
    return drives.split('\000')[:-1]


def format_date(timestamp, format="%Y-%m-%d %H:%M"):
    d = datetime.fromtimestamp(timestamp)
    return d.strftime(format)


def format_size(size):
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Y', suffix)

    return sizeof_fmt(size) if size != "" else ""


def is_hidden(x):
    attribute = x.stat().st_file_attributes
    path, fname = os.path.split(str(x))
    return bool(attribute & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM)) or str(fname).startswith(".")


def is_link(x):
    REPARSE_FOLDER = (stat.FILE_ATTRIBUTE_DIRECTORY | stat.FILE_ATTRIBUTE_REPARSE_POINT)
    if x.stat().st_file_attributes & REPARSE_FOLDER == REPARSE_FOLDER:
        return True
    return False




def q(text):
    return '"' + str(text) + '"'


def extension_to_bitmap(extension):
    """dot is mandatory in extension"""

    flags = shellcon.SHGFI_SMALLICON | \
            shellcon.SHGFI_ICON | \
            shellcon.SHGFI_USEFILEATTRIBUTES

    retval, info = shell.SHGetFileInfo(extension,
                                       FILE_ATTRIBUTE_NORMAL,
                                       flags)
    # non-zero on success
    assert retval

    hicon, iicon, attr, display_name, type_name = info

    # Get the bitmap
    icon = wx.Icon()
    icon.SetHandle(hicon)
    bmp = wx.Bitmap()
    bmp.CopyFromIcon(icon)
    return bmp
