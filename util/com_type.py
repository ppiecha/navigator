from collections import namedtuple, UserDict
from dataclasses import dataclass
from collections.abc import Callable

PathItem = namedtuple("PathItem", "lower_name date size name is_dir extension path")


@dataclass
class HotKey:
    id: int
    mod_key: int
    key: int
    action: Callable
    url: str
    caption: str

