from datetime import datetime
from win32com.shell import shell, shellcon
from win32con import FILE_ATTRIBUTE_NORMAL
import wx
import stat
import os
import win32api
import win32file
from pathlib import Path


def get_drives():

    drive_types = {
        0: "Unknown",
        1: "No Root Directory",
        2: "Removable Disk",
        3: "Local Disk",
        4: "Network Drive",
        5: "Compact Disc",
        6: "RAM Disk"
    }

    drives = (drive for drive in win32api.GetLogicalDriveStrings().split("\000") if drive)
    drive_dict = {}
    for drive in drives:
        try:
            info = win32api.GetVolumeInformation(drive)
        except:
            info = [""]
        # print(drive, "=>", drive_types[win32file.GetDriveType(drive)])
        drive_dict[drive] = [drive, info[0], drive_types[win32file.GetDriveType(drive)], drive]
    desk_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
    home_path = Path.home()
    drive_dict[desk_path] = ["Desktop", "", desk_path, desk_path]
    drive_dict[home_path] = ["Home", "", home_path, home_path]
    return drive_dict


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

