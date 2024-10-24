# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import time
import traceback
from dogtail.config import config

import logging
import inspect

"""
Logging facilities
"""

__author__ = """Ed Rousseau <rousseau@redhat.com>,
Zack Cerza <zcerza@redhat.com,
David Malcolm <dmalcolm@redhat.com>"""


class TimeStamp:
    """
    Timestamp class for file logs
    Generates timestamps tempfiles and log entries
    """

    def __init__(self):
        self.now = "0"
        self.timetup = time.localtime()


    def zeroPad(self, intt, width=2):
        """
        Pads an integer 'int' with zeroes, up to width 'width'.
        Returns a string.
        It will not truncate. If you call zeroPad(100, 2), '100' will be returned.
        """

        if intt < 10 ** width:
            return ("0" * (width - len(str(intt)))) + str(intt)

        return str(intt)


    def fileStamp(self, filename, addTime=True):
        """
        Generates a filename stamp in the format of filename_YYYYMMDD-hhmmss.
        A format of filename_YYYYMMDD can be used instead by specifying addTime = False.
        Should produce rel-eng style filestamps
        """

        self.now = filename.strip() + "_"
        self.timetup = time.localtime()

        fieldCount = 3
        if addTime:
            fieldCount = fieldCount + 3
        for i in range(fieldCount):
            if i == 3:
                self.now = self.now + "-"
            self.now = self.now + self.zeroPad(self.timetup[i])
        return self.now


    def entryStamp(self):
        """
        Generates a logfile entry stamp of YYYY.MM.DD HH:MM:SS
        """

        self.timetup = time.localtime()

        for i in range(6):
            if i == 0: # year
                self.now = str(self.timetup[i])
            elif i in (1, 2): # month day
                self.now = self.now + "." + self.zeroPad(self.timetup[i])
            else: # hour minutes seconds
                if i == 3:
                    self.now = self.now + " " + self.zeroPad(self.timetup[i])
                else:
                    self.now = self.now + ":" + self.zeroPad(self.timetup[i])

        return self.now


class Logger:
    """
    Writes entries to standard out.
    """

    stamper = TimeStamp()

    def __init__(self, logName, file=False, stdOut=True):
        """
        name: the name of the log
        file: The file object to log to.
        stdOut: Whether to log to standard out.
        """

        self.logName = logName
        self.stdOut = stdOut
        self.filee = file

        scriptName = config.scriptName

        if not scriptName:  # pragma: no cover
            scriptName = "log"

        self.fileName = scriptName

        if not self.filee:
            self.filee = False
            return

        if os.path.isdir(config.logDir):
            self.findUniqueName()
        else:
            raise IOError("Log path %s does not exist or is not a directory" % config.logDir)


    def findUniqueName(self):
        """
        Generate a logfile name and check if it already exists to obtain a unique one
        """

        self.fileName = config.logDir + self.stamper.fileStamp(self.fileName) + '_' + self.logName
        i = 0

        while os.path.exists(self.fileName):
            if i == 0:
                self.fileName = self.fileName + "." + str(i)
            else:
                logsplit = self.fileName.split(".")
                logsplit[-1] = str(i)
                self.fileName = ".".join(logsplit)
            i += 1


    def createFile(self):
        """
        Try to create the file and write the header info
        """

        print("Creating logfile at %s ..." % self.fileName)
        self.filee = open(self.fileName, mode="w")
        self.filee.write("##### " + os.path.basename(self.fileName) + "\n")
        self.filee.flush()


    def log(self, message, newline=True, force=False):
        """
        Hook used for logging messages. Might eventually be a virtual
        function, but nice and simple for now.

        If force is True, log to a file irrespective of config.logDebugToFile.
        """
        

        if isinstance(self.filee, bool) and (force or config.logDebugToFile):
            self.createFile()

        if force or config.logDebugToFile:
            if newline:
                self.filee.write(message + str("\n"))
            else:
                self.filee.write(message + str(" "))
            self.filee.flush()

        if self.stdOut and config.logDebugToStdOut:
            try:
                print(message)
            except TypeError:
                print(message.decode("utf-8", "replace"))

class ResultsLogger(Logger):
    """
    Writes entries into the Dogtail log
    """

    def __init__(self, stdOut=True):
        Logger.__init__(self, "results", file=True, stdOut=stdOut)


    def log(self, entry):
        """
        Writes the log entry. Requires a 1 {key: value} pair dict for an argument or else it will
        throw an exception.
        """

        if len(entry) == 1:
            key = list(entry.keys())
            value = list(entry.values())
            key = key[0]
            value = value[0]
            entry = str(key) + ":      " + str(value)
        else:
            print("Method argument requires a 1 {key: value} dict. Supplied argument not one {key: value}")
            raise ValueError(entry)

        Logger.log(self, self.stamper.entryStamp() + "      " + entry, force=True)

debugLogger = Logger("debug", config.logDebugToFile)


def exceptionHook(exc, value, tb):  # pragma: no cover
    tbStringList = traceback.format_exception(exc, value, tb)
    tbString = "".join(tbStringList)
    debugLogger.log(tbString)

sys.excepthook = exceptionHook


### Logging definition for debugging dogtail itself.
### Can be used in other parts, but we cannot break the api.

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DebugLogger(metaclass=Singleton):
    logger = None

    def __init__(self):
        # Using logging.basicConfig can negatively affect all other (3rd party)
        # already instantiated loggers
        self.logger = logging.getLogger("debug")
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(streamHandler)


    @staticmethod
    def __get_call_info():
        stack = inspect.stack()

        file_name = stack[3][1].split("/")[-1]
        line_length = stack[3][2]

        return file_name, line_length


    def info(self, message, *args):
        message = "[{}:{:3}] {}".format(*self.__get_call_info(), message)
        self.logger.info(message, *args)

try:
    DEBUG_DOGTAIL = os.environ["DOGTAIL_DEBUG"] == "true"
except KeyError:
    DEBUG_DOGTAIL = False

_log = DebugLogger()
def debug_log(message):
    if DEBUG_DOGTAIL:
        _log.info(message)
