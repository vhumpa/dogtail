"""Wrapper code to help when scripting Konqueror

Author: David Malcolm <dmalcolm@redhat.com>"""

__author__ = 'David Malcolm <dmalcolm@redhat.com>'

from dogtail.tree import *
from dogtail.distro import packageDb
from dogtail.apps.categories import *

class KonquerorApp(ApplicationRef, FileBrowser, WebBrowser):
    """Utility wrapper for Konqueror; implements the FileBrowser and WebBrowser mixin interfaces"""
