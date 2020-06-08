import sys
import wx
import tabs
import pickle


CN_APP_CONFIG = "viewer.dat"


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Viewer", size=(500, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.app_props = AppProps()
        self.book = tabs.EditorBook(frame=self)
        # self.book.add_tab("main_frame.py")

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.Init()

    def Init(self):
        self.app_props = self.read_last_conf(CN_APP_CONFIG, self.app_props)
        if self.app_props.pos:
            self.SetPosition(self.app_props.pos)
        else:
            self.Center()
        self.SetSize(self.app_props.size)
        self.process_args()

    def on_close(self, e):
        self.write_last_conf(CN_APP_CONFIG, self.app_props)
        e.Skip()

    def process_args(self):
        if len(sys.argv) > 1:
            opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
            args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
            if args:
                for f_name in args:
                    self.book.add_tab(f_name, "-r" in opts)
        else:
            self.book.add_tab()

    def read_last_conf(self, conf_file, app_conf):
        try:
            with open(conf_file, 'rb') as ac:
                return pickle.load(ac)
        except IOError:
            # self.log_error("Cannot read app configuration '%s'." % conf_file)
            return app_conf

    def write_last_conf(self, conf_file, app_conf):
        try:
            app_conf.size = self.GetSize()
            app_conf.pos = self.GetPosition()
            with open(conf_file, 'wb') as ac:
                pickle.dump(app_conf, ac)
        except IOError:
            wx.LogError("Cannot save project file '%s'." % conf_file)


class AppProps:
    def __init__(self):
        self.pos = None
        self.size = (500, 400)




