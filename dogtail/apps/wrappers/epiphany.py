"""Wrapper code to help when scripting Epiphany

Author: David Malcolm <dmalcolm@redhat.com>"""

__author__ = 'David Malcolm <dmalcolm@redhat.com>'

from dogtail.tree import *
from dogtail.distro import *
from dogtail.apps.categories import *

class EpiphanyApp(Application, WebBrowser):
	"""Utility wrapper for Epiphany; implements the Webbrowser mixin interface"""

	def __init__(self):
		Application.__init__(self, root.application("epiphany"))

		if isinstance(distro, Debian):
			self.epiPackageName="epiphany-browser"
		else:
			self.epiPackageName="epiphany"
		self.epiVersion = packageDb.getVersion(self.epiPackageName)
		print "Epiphany version %s"%self.epiVersion

	def browseToUrl(self, urlString):
		# Click on File->New Tab on some epiphany window:
		newTabMenuItem = self.menu("File").menuItem("New Tab")
		newTabMenuItem.click()

		window = EpiphanyWindow(newTabMenuItem.findAncestor(predicate.IsAWindow()))

		tabs = window.tabs()

		# Set URL:
		print window.urlEntry().extents
		window.urlEntry().text = urlString
		window.urlEntry().activate()

		# This is in the final tab; return it:
		return tabs[-1]

class EpiphanyWindow(Window):
	def __init__(self, node):
		Window.__init__(self, node)
		self.pageTabList = self.child(roleName='page tab list', debugName='Page Tab List')

	def tabs(self):
		"""
		FIXME: not true: Get all tabs of this window as a list of EpiphanyTab instances
		"""
		return self.pageTabList.findChildren (predicate.GenericPredicate(roleName='page tab'), recursive=True)

	def urlEntry(self):
		"""
		Get the text entry Node for entering URLs.
		FIXME: this is currently something of a hack
		"""
		# FIXME: we hope that this gives us the correct text entry:
		return self.child(roleName='text', debugName='URL Entry')

#	 def newTab(self, url):
		
	
#class EpiphanyTab(Node):
#	 def __init__(self, node, window):
#		 Node.__init__(self, node)
#		 self.window = window
