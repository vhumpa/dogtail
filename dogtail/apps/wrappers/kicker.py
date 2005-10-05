"""Wrapper code to help when scripting Kicker, the KDE panel

Author: David Malcolm <dmalcolm@redhat.com>"""

__author__ = 'David Malcolm <dmalcolm@redhat.com>'

from dogtail.tree import *
from dogtail.distro import packageDb
from dogtail.apps.categories import *

class Kicker(ApplicationRef, DesktopPanel):
		"""Utility wrapper for Kicker, the KDE panel; implements the DesktopPanel mixin interface"""

