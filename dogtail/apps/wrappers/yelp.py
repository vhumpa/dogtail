"""Wrapper code to help when scripting yelp

Author: David Malcolm <dmalcolm@redhat.com>"""

__author__ = 'David Malcolm <dmalcolm@redhat.com>'

from dogtail.tree import *
from dogtail.distro import packageDb
from dogtail.apps.categories import *
from dogtail.version import Version

class YelpApp(Application):
	def __init__(self):
		Application.__init__(self, root.application("gnome-help"))

		self.version = packageDb.getVersion("yelp")
		
		print "yelp version %s"%self.version
	
	def checkError(self):
		"""
		Look for error dialogs, raising an error if one is found.
		"""
		errorDlg = self.findChild(predicate.GenericPredicate(name="Error", roleName="alert"), requireResult=False)
		if errorDlg!=None:
			msg = ""
			for text in errorDlg.findChildren(predicate.GenericPredicate(roleName='label')):
				msg += text.text
			raise msg
	
	def window(self):
		"""
		Find a window of the app
		"""
		return self.findChild(predicate.GenericPredicate(roleName="frame"))

	def ensureLoadingComplete(self):
		"""
		Wait for yelp to stop having "Loading..." as a title
		"""
		window = self.window()

		numWaits = 0
		
		# FIXME: i18n issues!
		while window.name =='Loading...':
			sleep(5)
			if ++numWaits > 20:
				raise "Yelp took too long to open help"
		
				
def checkAppHelp(app):
	"""
	Click on Help->Contents and check that help comes up properly.
	"""
	app.menu('Help').menuItem('Contents').click()

	yelp = YelpApp()
	yelp.ensureLoadingComplete()
	yelp.checkError()
