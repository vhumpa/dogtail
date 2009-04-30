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

class XServer(object):
    def __init__(self, binary = "/usr/bin/Xorg", 
            xinitrc = "/etc/X11/xinit/Xclients", 
            resolution = "1024x768x16"):
        """resolution is only used with Xvfb."""
        self.xinit = "/usr/bin/xinit"
        self.display = None
        self.binary = binary
        self.xinitrc = xinitrc
        self.resolution = resolution
        self.exitCode = None
        self.running = False

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

    def _buildCommand(self):
        self.display = self.findFreeDisplay()
        cmd = []
        if self.xinit:
            cmd.append(self.xinit)
            if self.xinitrc: cmd.append(self.xinitrc)
            cmd.append('--')
        cmd.append(self.binary)
        cmd.append(self.display)
        cmd.extend(['-ac', '-noreset'])
        if self.binary.endswith('Xvfb'):
            cmd.extend(['-screen', '0', self.resolution])
            cmd.append('-shmem')
        return cmd

    def start(self):
        cmd = self._buildCommand()
        print ' '.join(cmd)
        self.popen = subprocess.Popen(cmd)
        self.running = True
        return self.popen.pid

    def wait(self):
        self.exitCode = self.popen.wait()
        self.running = False
        return self.exitCode

    def stop(self):
        self.popen.terminate()
        self.running = False

class Script(object):
    def __init__(self, name, args = []):
        self.name = name
        self.args = args
        self.popen = None
        self.exitCode = None

    def start(self, environ = None):
        if environ == None: environ = os.environ
        self.popen = subprocess.Popen(self.args, executable = self.name,
                env = environ)#, stdout = subprocess.PIPE, 
                #stderr = subprocess.STDOUT, close_fds = True)
        self.running = True
        return self.popen.pid

    def wait(self):
        self.exitCode = self.popen.wait()
        self.running = False
        return self.exitCode

    def stop(self):
        self.popen.terminate()
        self.running = False


class Session(object):

    cookieName = "DOGTAIL_SESSION_COOKIE"

    def __init__(self, sessionBinary, scriptName, scriptArgs = [], scriptDelay = 10, logout = True):
        self.sessionBinary = sessionBinary
        self.script = Script(scriptName, scriptArgs)
        self.scriptDelay = scriptDelay
        self.logout = logout
        self.xserver = XServer()
        self.__cookie = None
        self.__environment = None
        self.exitCodeFile = scratchFile("exitcode").name

    def start(self):
        xinitrcFileObj = scratchFile('xinitrc')
        self.xserver.xinitrc = xinitrcFileObj.name
        self._buildXInitRC(xinitrcFileObj)
        xServerPid = self.xserver.start()
        time.sleep(self.scriptDelay)
        scriptEnv = self.environment
        scriptPid = self.script.start(scriptEnv)
        return (xServerPid, scriptPid)

    @property
    def environment(self):
        if self.__environment: return self.__environment
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
            if isSessionEnv(envDict): self.__environment = envDict
        if not self.__environment:
            raise RuntimeError("Can't find our environment!")
        return self.__environment

    def wait(self):
        self.script.wait()
        return self.xserver.wait()

    def stop(self):
        self.script.stop()
        self.xserver.stop()

    def attemptLogout(self):
        logoutScript = Script('/tmp/dt_git/scripts/dogtail-logout')
        logoutScript.start(environ = self.environment)
        logoutScript.wait()

    @property
    def cookie(self):
        if not self.__cookie:
            self.__cookie = "%X" % random.getrandbits(16)
        return self.__cookie

    @property
    def running(self):
        return self.xserver.running

    @property
    def scriptExitCode(self):
        if self.running: self.wait()
        try:
            return int(file(self.exitCodeFile, 'r').read())
        except ValueError:
            return None

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
            #"sh -c \"sleep 10; cd %s && dogtail-detect-session && sh -c \\\"%s; echo -n \\\\\\$? > %s\\\"%s\"&\n" % (os.getcwdu(), self.script, self.exitCodeFile, logoutString),
            "exec -l $SHELL -c \"$CK_XINIT_SESSION $SSH_AGENT %s\"" % \
                    self.sessionBinary,
            ""]

        fileObj.write('\n'.join(lines).strip())
        fileObj.flush()
        fileObj.close()
