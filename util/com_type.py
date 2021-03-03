from collections import namedtuple

PathItem = namedtuple("PathItem", "lower_name date size name is_dir extension path")
HotKey = namedtuple("HotKey", "id mod_key key action")