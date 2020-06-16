import wx

class Links:
    def __init__(self):
        pages = {"Links": []}


class SimpleLinkItem:
    """
    Dir
    File
    Hyper Link
    Command
    """
    def __init__(self, name, target, params=[]):
        self.name = name
        self.target = target
        self.params = params
