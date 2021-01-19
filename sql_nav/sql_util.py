import os
import wx
from enum import Enum
from typing import List, Optional
import cx_Oracle as oracle


SQL_KEYWORDS = ['select', 'insert', 'update', 'delete', 'create', 'replace', 'table', 'schema', 'not', 'null',
                'primary', 'key', 'unique', 'index', 'constraint', 'check', 'or', 'and', 'on', 'foreign', 'references',
                'cascade', 'default', 'grant', 'usage', 'to', 'is', 'restrict', 'into', 'values', 'from', 'where',
                'group',
                'by', 'join', 'left', 'right', 'outer', 'having', 'distinct', 'as', 'limit', 'like', 'order',
                'begin', 'end', 'declare', 'exception', 'raise', 'type', 'procedure', 'function', 'package',
                'return', 'bulk', 'collect', 'into']


class ConnectionInfo:
    def __init__(self, user: str, password: str, host: str, port: int, service_name: str):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.service_name = service_name
        self.connections = {}

    def get_sql_plus_str(self) -> str:
        return self.user + "/" + self.password + "@" + self.host + ":" + str(self.port) + "/" + self.service_name

    def get_dsn(self) -> str:
        return oracle.makedsn(host=self.host, port=self.port, service_name="orcl")

    def __str__(self):
        return self.user + "@" + self.host + ":" + str(self.port) + "/" + self.service_name


class SQLMode(Enum):
    SQL = "SQL"
    PLSQL = "PLSQL"
    SQLPLUS = "SQLPLUS"


class Cmd:
    def __init__(self, cmd: str, mode: SQLMode = SQLMode.SQLPLUS) -> None:
        self.cmd = cmd
        self.mode = mode

    def set_cmd(self, cmd: str) -> None:
        self.cmd = cmd

    def __str__(self):
        return str(self.mode) + " " + self.cmd


CmdList = List[Cmd]


def format_error(e: oracle.DatabaseError) -> str:
    error, = e.args
    return error.message


def is_plsql_cmd(first_word: str) -> bool:
    return first_word.lower() in ["create", "begin", "declare"]


def is_sql_cmd(first_word: str) -> bool:
    return first_word.lower() in ["select", "with", "alter", "drop"]


def is_line_empty(line_str: str) -> bool:
    line_str = line_str.strip()
    return line_str == "" or line_str.startswith("--") or line_str.startswith("/*")


def prepare_cmd(cmd_str: str) -> Optional[Cmd]:
    mode: SQLMode
    cmd_str = os.linesep.join([s for s in cmd_str.splitlines() if s.strip()])
    cmd_str = cmd_str.strip()
    first_word: List = cmd_str.split(maxsplit=1)
    if first_word:
        if is_plsql_cmd(first_word=first_word[0]):
            if cmd_str.endswith(";"):
                cmd_str += "\n/"
            mode = SQLMode.PLSQL
        elif is_sql_cmd(first_word=first_word[0]):
            if not cmd_str.endswith(";"):
                cmd_str += ";"
            mode = SQLMode.SQL
        else:
            if cmd_str.endswith(";"):
                cmd_str = cmd_str.rstrip(";")
            mode = SQLMode.SQLPLUS
        return Cmd(cmd=cmd_str, mode=mode)
    else:
        return None


class Splitter(wx.SplitterWindow):
    def __init__(self, parent):
        super().__init__(parent=parent, style=wx.SP_BORDER | wx.SP_LIVE_UPDATE)


