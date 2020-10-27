import logging
import threading
import time
from subprocess import Popen, PIPE, TimeoutExpired
from typing import List, Tuple

import wx

from sql_nav.out_editor import SQLOutCtrl
from sql_nav.sql_editor import SQLMode, CmdList, Cmd
from lib4py import logger as lg

logger = lg.get_console_logger(name=__name__, log_level=logging.DEBUG)


class SQLEng:
    def __init__(self, sql_out: SQLOutCtrl, sql_grid=None) -> None:
        self.sql_out: SQLOutCtrl = sql_out
        self.sql_grid = sql_grid
        self.process: Popen = None
        self._connection_str: str = ""
        self._connected: bool = False

        self.output_thread = threading.Thread(target=self.print_output, args=[])
        self.output_thread.start()

    def kill_process(self):
        if self.process:
            logger.debug("Killing process " + str(self.process.pid))
            self.process.kill()

    def close(self):
        logger.debug("closing: " + str(self))
        self.exit_sql_plus()
        self.close_input_output()
        self.output_thread.join()
        self.process.terminate()
        logger.debug(str(self.process.pid) + " " +
                     str("still alive" if self.process.returncode is None else "terminated"))
        if self.process.returncode is None:
            raise ValueError("Process not terminated properly")

    @property
    def connection_str(self):
        if not self._connection_str:
            raise ValueError("Connection string not defined")
        return self._connection_str

    @connection_str.setter
    def connection_str(self, value):
        self._connection_str = value

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value: bool):
        self._connected = value

    def start_sql_plus(self):
        self.process = Popen(["sqlplus", "/NOLOG"], stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
        self.init_sql_plus()

    def connect_sql_plus(self):
        self._exec_in_sql_plus(cmd=Cmd(cmd="connect " + self.connection_str))

    def init_sql_plus(self) -> None:
        self._exec_in_sql_plus(cmd=Cmd(cmd="set sqlprompt ''"))
        self._exec_in_sql_plus(cmd=Cmd(cmd="set sqlnumber off"))
        self._exec_in_sql_plus(cmd=Cmd(cmd="set serveroutput on"))
        wx.CallLater(1000, self.sql_out.append, "Server output set to ON")

    def exit_sql_plus(self) -> None:
        if self.process.returncode is None:
            try:
                out, err = self.process.communicate(input="exit\n", timeout=1)
                self.sql_out.append(out)
                self.sql_out.append(err)
            except TimeoutExpired:
                logger.debug("Process termination timeout")
                self.process.kill()
                out, err = self.process.communicate()
        self.connected = False

    def close_input_output(self):
        if not self.process.stdin.closed:
            self.process.stdin.close()
        if not self.process.stdout.closed:
            self.process.stdout.close()

    def _exec_in_sql_plus(self, cmd: Cmd) -> None:
        if not cmd:
            raise ValueError("Empty command")
        cmd.set_cmd(cmd.cmd.rstrip())
        if not cmd.cmd.endswith("\n"):
            cmd.set_cmd(cmd.cmd + "\n")
        if cmd.mode in (SQLMode.PLSQL, SQLMode.SQL):
            self.process.stdin.write("clear buffer\n")
            if not self.connected:
                self.sql_out.print_error(error="Not connected to Oracle")
                return
        if not self.process:
            raise ValueError("Process not active")
        if self.process.stdin.closed:
            raise ValueError("STDIN closed")
        self.process.stdin.write(cmd.cmd)
        self.process.stdin.flush()

    def exec_in_sql_plus(self, cmd_list: CmdList, edit_mode: int) -> None:
        for cmd in cmd_list:
            self._exec_in_sql_plus(cmd=cmd)

    def print_output(self) -> None:
        while True:
            time.sleep(0.01)
            if self.process:
                if self.process.stdout.closed:
                    logger.debug("exiting output thread")
                    break
                output: str
                try:
                    output = self.process.stdout.readline()
                except ValueError as e:
                    logger.debug(str(e))
                if self.process.poll() is not None:
                    break
                if output and self.sql_out:
                    if "Connected" in output:
                        self.connected = True
                    if "Disconnected" in output:
                        self.connected = False
                    wx.CallAfter(self.sql_out.append, output)
        # rc = self.process.poll()
