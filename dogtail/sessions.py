import os
import re
import subprocess
import tempfile
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

class Session(object):
    def __init__(self, script):
        self.xserver = XServer()
        self.script = script
        self.exitCodeFile = scratchFile("exitcode").name

    def start(self):
        xinitrcFileObj = scratchFile('xinitrc')
        self.xserver.xinitrc = xinitrcFileObj.name
        self._buildXInitRC(xinitrcFileObj)
        return self.xserver.start()

    def wait(self):
        return self.xserver.wait()

    def stop(self):
        self.xserver.stop()

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


class GNOMESession(Session):
    gnome_session = "/usr/bin/gnome-session"
    def __init__(self, script, logout = True):
        Session.__init__(self, script)
        self.logout = logout

    def _buildXInitRC(self, fileObj):
        if self.logout:
            logoutString = "; dogtail-logout"
        else:
            logoutString = ""
        lines = [
            "gconftool-2 --type bool --set /desktop/gnome/interface/accessibility true",
            ". /etc/X11/xinit/xinitrc-common",
            "sh -c \"sleep 10; cd %s && dogtail-detect-session && sh -c \\\"%s; echo -n $? > %s\\\"%s\"&\n" % (os.getcwdu(), self.script, self.exitCodeFile, logoutString),
            "exec -l $SHELL -c \"$CK_XINIT_SESSION $SSH_AGENT %s\"" % \
            #"$CK_XINIT_SESSION $SSH_AGENT %s &" % \
                    self.gnome_session,
            #"sleep 10",
            #"cd %s && dogtail-detect-session && sh -c \"%s\"; echo -n $? > %s\n" % (os.getcwdu(), self.script, self.exitCodeFile),
            ""]
        fileObj.write('\n'.join(lines).strip())
        fileObj.flush()
        fileObj.close()


