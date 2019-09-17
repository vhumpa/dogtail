# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import unittest


class GtkDemoTest(unittest.TestCase):
    """
    TestCase subclass which handles bringing up and shutting down gtk3-demo as a fixture.  Used for writing other test
    cases.
    """

    def setUp(self):
        import dogtail.config
        dogtail.config.config.logDebugToStdOut = True
        dogtail.config.config.logDebugToFile = False
        import dogtail.utils
        self.pid = dogtail.utils.run('gtk3-demo')
        self.app = dogtail.tree.root.application('gtk3-demo')

    def tearDown(self):
        import os
        import signal
        import time
        os.kill(self.pid, signal.SIGKILL)
        os.system('killall gtk3-demo-application > /dev/null 2>&1')
        os.system('killall gtk3-demo > /dev/null 2>&1')
        # Sleep just enough to let the app actually die.
        # AT-SPI doesn't like being hammered too fast.
        time.sleep(0.5)

    def runDemo(self, demoName, retry=True):
        """
        Click on the named demo within the gtk3-demo app.
        """
        tree = self.app.child(roleName="tree table")
        tree.child(demoName, retry=retry).doActionNamed('activate')


def trap_stdout(function, args=None):
    """
    Grab stdout output during function execution
    """

    import sys
    from io import StringIO

    saved_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out
        if type(args) is dict:
            function(**args)
        elif args:
            function(args)
        else:
            function()
        output = out.getvalue().strip()
    finally:
        sys.stdout = saved_stdout
    return output
