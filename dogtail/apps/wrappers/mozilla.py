"""Wrapper code to help when scripting Mozilla apps

Author: David Malcolm <dmalcolm@redhat.com>"""

__author__ = 'David Malcolm <dmalcolm@redhat.com>'

from dogtail.tree import *
from dogtail.distro import packageDb
from dogtail.apps.categories import *

class MozillaApp(Application):
    """Useful test hooks for mozilla application testcases (Firefox, Thunderbird)"""
    def __init__(self):
        Application.__init__(self, root.application("mozilla"))

        self.mozVersion = packageDb.getVersion("firefox")
        print "Firefox version %s"%self.mozVersion

class FirefoxApp(MozillaApp, WebBrowser):
    """Utility wrapper for Firefox; implements the Webbrowser mixin interface"""

class ThunderbirdApp(MozillaApp, EmailClient):
    """Utility wrapper for Thunderbird; implements the EmailClient mixin interface"""
