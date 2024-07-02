# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import time
import os
import pwd
import errno
import re
import subprocess
import tempfile
import random
import glob
from dogtail.config import config
from dogtail.logging import debug_log


def scratchFile(label):  # pragma: no cover
    """
    Uses tempfile.NamedTemporaryFile() to create a unique tempfile in config.scratchDir
    with a filename like: dogtail-headless-<label>.<random junk>
    """

    debug_log("scratchFile(label=%s)" % label)

    prefix = "dogtail-headless-%s." % label
    return tempfile.NamedTemporaryFile(prefix=prefix, dir=config.scratchDir, mode="w")


def testBinary(path):  # pragma: no cover
    """
    Test if given binary file exists.
    """

    debug_log("testBinary(path=%s)" % str(path))

    if (path.startswith(os.path.sep) or
            path.startswith(os.path.join(".", "")) or
            path.startswith(os.path.join("..", ""))):
        if not os.path.exists(path):
            raise IOError(errno.ENOENT, "No such file", path)

        if not os.access(path, os.X_OK):
            raise IOError(errno.ENOEXEC, "Permission denied", path)

    return True


def get_username():  # pragma: no cover
    """
    Returns a user name.
    """

    debug_log("get_username()")

    return pwd.getpwuid(os.getuid())[0]


class Subprocess:  # pragma: no cover
    """
    Subprocess class definition.
    """

    def __init__(self, cmdList, environ=None):
        testBinary(cmdList[0])
        self.cmdList = cmdList
        self.environ = environ
        self._exitCode = None


    def start(self):
        debug_log("Subprocess.start - execute the command through Popen.")

        if self.environ is None:
            self.environ = os.environ

        self.popen = subprocess.Popen(self.cmdList, env=self.environ)

        return self.popen.pid


    def wait(self):
        debug_log("Subprocess.wait - wait until Popen execution is done.")

        return self.popen.wait()


    def stop(self):
        debug_log("Subprocess.stop - terminate Popen object.")

        self.popen.terminate()


    @property
    def exitCode(self):
        debug_log("Subprocess.exitCode - returning exit code.")

        if self._exitCode is None:
            self._exitCode = self.wait()
        return self._exitCode


class XServer(Subprocess):  # pragma: no cover
    """
    XServer class definition inheriting from Subprocess class.
    """

    def __init__(self, server="/usr/bin/Xorg",
                 xinitrc="/etc/X11/xinit/Xclients",
                 resolution="1024x768x16"):
        testBinary(server)
        self.server = server
        self._exitCode = None
        self.xinit = "/usr/bin/xinit"
        self.display = None
        self.xinitrc = xinitrc
        self.resolution = resolution


    @staticmethod
    def findFreeDisplay():
        debug_log("findFreeDisplay()")

        tmp = os.listdir("/tmp")
        pattern = re.compile(".X([0-9]+)-lock")
        usedDisplays = []
        for file in tmp:
            match = re.match(pattern, file)
            if match:
                usedDisplays.append(int(match.groups()[0]))
        if not usedDisplays:
            return ":0"
        usedDisplays.sort()
        return ":" + str(usedDisplays[-1] + 1)


    @property
    def cmdList(self):
        debug_log("cmdList(self)")

        self.display = self.findFreeDisplay()

        cmd = []
        if self.xinit:
            cmd.append(self.xinit)
            if self.xinitrc:
                cmd.append(self.xinitrc)
            cmd.append("--")

        cmd.append(self.server)
        cmd.append(self.display)
        cmd.extend(["-ac", "-noreset"])

        if self.server.endswith("Xvfb"):
            cmd.extend(["-screen", "0", self.resolution])
            cmd.append("-shmem")

        return cmd


    def start(self):
        debug_log("XServer.start - starts process with command from XServer.cmdList.")

        print(' '.join(self.cmdList))
        self.popen = subprocess.Popen(self.cmdList)
        return self.popen.pid


class Script(Subprocess):  # pragma: no cover
    pass


class Session:  # pragma: no cover
    """
    Session class definition.
    """

    cookieName = "DOGTAIL_SESSION_COOKIE"

    def __init__(self, sessionBinary, scriptCmdList=[], scriptDelay=20, logout=True):
        testBinary(sessionBinary)
        self.sessionBinary = sessionBinary
        self.script = Script(scriptCmdList)
        self.scriptDelay = scriptDelay
        self.logout = logout
        self.xserver = XServer()
        self._cookie = None
        self._environment = None


    def start(self):
        debug_log("Session.start - starts a process via XServer.start")

        self.xinitrcFileObj = scratchFile("xinitrc")
        self.xserver.xinitrc = self.xinitrcFileObj.name
        self._buildXInitRC(self.xinitrcFileObj)
        xServerPid = self.xserver.start()
        time.sleep(self.scriptDelay)
        self.script.environ = self.environment
        scriptPid = self.script.start()

        return (xServerPid, scriptPid)


    @property
    def environment(self):
        debug_log("Session.environment - returns an environment")

        def isSessionProcess(fileName):
            debug_log("isSessionProcess(fileName=%s)" % str(fileName))

            try:
                if self.sessionBinary.split("/")[-1] == "startkde":
                    path_to_compare = "/usr/bin/plasma-desktop"
                else:
                    path_to_compare = self.sessionBinary

            except OSError:
                return False

            pid = fileName.split("/")[2]
            if pid == "self" or pid == str(os.getpid()):
                return False

            return True


        def getEnvDict(fileName):
            debug_log("getEnvDict(fileName=%s)" % str(fileName))

            try:
                with open(fileName, "r") as f:
                    envString = f.read()
            except IOError:
                return {}

            envItems = envString.split("\x00")
            envDict = {}

            for item in envItems:
                if "=" not in item:
                    continue
                k, v = item.split("=", 1)
                envDict[k] = v

            return envDict


        def isSessionEnv(envDict):
            debug_log("isSessionEnv(envDict=%s)" % str(envDict))
            if not envDict:
                return False

            if envDict.get(self.cookieName, "notacookie") == self.cookie:
                return True

            return False


        for path in glob.glob("/proc/*/"):
            if not isSessionProcess(path):
                continue

            envFile = path + "environ"
            envDict = getEnvDict(envFile)
            if isSessionEnv(envDict):
                self._environment = envDict

        if not self._environment:
            raise RuntimeError("Can't find our environment!")

        return self._environment


    def wait(self):
        debug_log("Session.stop - executes the XServer.wait method.")

        self.script.wait()
        return self.xserver.wait()


    def stop(self):
        debug_log("Session.stop - executes the XServer.stop method.")

        try:
            self.script.stop()
        except OSError:
            pass

        self.xserver.stop()


    def attemptLogout(self):
        debug_log("Session.attemptLogout - attempts to logout from session.")

        logoutScript = Script("dogtail-logout", environ=self.environment)
        logoutScript.start()
        logoutScript.wait()


    @property
    def cookie(self):
        debug_log("Session.cookie - returns a cookie attribute.")

        if not self._cookie:
            self._cookie = "%X" % random.getrandbits(16)
        return self._cookie


    def _buildXInitRC(self, fileObj):
        lines = [
            "export %s=%s" % (self.cookieName, self.cookie),
            "gsettings set org.gnome.desktop.interface toolkit-accessibility true",
            ". /etc/X11/xinit/xinitrc-common",
            "export %s" % self.cookieName,
            "exec -l $SHELL -c \"$CK_XINIT_SESSION $SSH_AGENT %s\"" %
            (self.sessionBinary),
            ""]

        fileObj.write("\n".join(lines).strip())
        fileObj.flush()
