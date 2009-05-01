import time
import os
import re
import subprocess
import tempfile
import random
import glob
from dogtail.config import config

def scratchFile(label):
    """Uses tempfile.NamedTemporaryFile() to create a unique tempfile in 
    config.scratchDir, with a filename like: 
    dogtail-headless-<label>.<random junk>"""
    prefix = "dogtail-headless-"
    return tempfile.NamedTemporaryFile(prefix = "%s%s." % (prefix, label), 
            dir = config.scratchDir, delete = False)

class Subprocess(object):
    def __init__(self, cmdList, environ = None):
        self.cmdList = cmdList
        self.environ = environ
        self._exitCode = None

    def start(self):
        if self.environ == None: environ = os.environ
        self.popen = subprocess.Popen(self.cmdList,
                env = self.environ)#, stdout = subprocess.PIPE, 
                #stderr = subprocess.STDOUT, close_fds = True)
        return self.popen.pid

    def wait(self):
        return self.popen.wait()

    def stop(self):
        self.popen.terminate()

    @property
    def exitCode(self):
        if self._exitCode == None:
            self._exitCode = self.wait()
        return self._exitCode

class XServer(Subprocess):
    def __init__(self, server = "/usr/bin/Xorg", 
            xinitrc = "/etc/X11/xinit/Xclients", 
            resolution = "1024x768x16"):
        """resolution is only used with Xvfb."""
        self.server = server
        self._exitCode = None
        self.xinit = "/usr/bin/xinit"
        self.display = None
        self.xinitrc = xinitrc
        self.resolution = resolution

    @staticmethod
    def findFreeDisplay():
        tmp = os.listdir('/tmp')
        pattern = re.compile('\.X([0-9]+)-lock')
        usedDisplays = []
        for file in tmp:
            match = re.match(pattern, file)
            if match: usedDisplays.append(int(match.groups()[0]))
        if not usedDisplays: return ':0'
        usedDisplays.sort()
        return ':' + str(usedDisplays[-1] + 1)

    @property
    def cmdList(self):
        self.display = self.findFreeDisplay()
        cmd = []
        if self.xinit:
            cmd.append(self.xinit)
            if self.xinitrc: cmd.append(self.xinitrc)
            cmd.append('--')
        cmd.append(self.server)
        cmd.append(self.display)
        cmd.extend(['-ac', '-noreset'])
        if self.server.endswith('Xvfb'):
            cmd.extend(['-screen', '0', self.resolution])
            cmd.append('-shmem')
        return cmd

    def start(self):
        print ' '.join(self.cmdList)
        self.popen = subprocess.Popen(self.cmdList)
        return self.popen.pid

class Script(Subprocess):
    pass

class Session(object):

    cookieName = "DOGTAIL_SESSION_COOKIE"

    def __init__(self, sessionBinary, scriptCmdList, scriptDelay = 10, logout = True):
        self.sessionBinary = sessionBinary
        print scriptCmdList
        self.script = Script(scriptCmdList)
        self.scriptDelay = scriptDelay
        self.logout = logout
        self.xserver = XServer()
        self._cookie = None
        self._environment = None

    def start(self):
        xinitrcFileObj = scratchFile('xinitrc')
        self.xserver.xinitrc = xinitrcFileObj.name
        self._buildXInitRC(xinitrcFileObj)
        xServerPid = self.xserver.start()
        time.sleep(self.scriptDelay)
        self.script.environ = self.environment
        scriptPid = self.script.start()
        return (xServerPid, scriptPid)

    @property
    def environment(self):
        if self._environment: return self._environment
        def getEnvDict(fileName):
            try: envString = open(fileName, 'r').read()
            except IOError: return {}
            envItems = envString.split('\x00')
            envDict = {}
            for item in envItems:
                if not '=' in item: continue
                k, v = item.split('=', 1)
                envDict[k] = v
            return envDict

        def isSessionEnv(envDict):
            if not envDict: return False
            if envDict.get(self.cookieName, 'notacookie') == self.cookie:
                return True
            return False

        for envFile in glob.glob('/proc/*/environ'):
            pid = envFile.split('/')[2]
            if pid == 'self' or pid == str(os.getpid()): continue
            envDict = getEnvDict(envFile)
            if isSessionEnv(envDict): self._environment = envDict
        if not self._environment:
            raise RuntimeError("Can't find our environment!")
        return self._environment

    def wait(self):
        self.script.wait()
        return self.xserver.wait()

    def stop(self):
        try: self.script.stop()
        except OSError: pass
        self.xserver.stop()

    def attemptLogout(self):
        logoutScript = Script('/tmp/dt_git/scripts/dogtail-logout', 
                environ = self.environment)
        logoutScript.start()
        logoutScript.wait()

    @property
    def cookie(self):
        if not self._cookie:
            self._cookie = "%X" % random.getrandbits(16)
        return self._cookie

    def _buildXInitRC(self, fileObj):
        if self.logout:
            logoutString = "; dogtail-logout"
        else:
            logoutString = ""
        lines = [
            "export %s=%s" % (self.cookieName, self.cookie),
            "gconftool-2 --type bool --set /desktop/gnome/interface/accessibility true",
            ". /etc/X11/xinit/xinitrc-common",
            "export %s" % self.cookieName,
            "exec -l $SHELL -c \"$CK_XINIT_SESSION $SSH_AGENT %s\"" % \
                    self.sessionBinary,
            ""]

        fileObj.write('\n'.join(lines).strip())
        fileObj.flush()
        fileObj.close()

