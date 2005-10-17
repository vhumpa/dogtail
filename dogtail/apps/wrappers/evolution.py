"""Wrapper code to help when scripting Evolution

Author: David Malcolm <dmalcolm@redhat.com>"""

__author__ = 'David Malcolm <dmalcolm@redhat.com>'

from dogtail.tree import *
from dogtail.procedural import *
from dogtail.utils import run
from os import environ, path, remove

from dogtail.distro import *
from dogtail.version import Version

from dogtail.apps.categories import *

# Evolution folder browser (GtkTreeView?) seems to be implemented as a list of role='table cell' children (the rows), with each having a list of 'table cell' children (the table cells)
# The table rows have NODE_CHILD_OF relations (with paths, in at-poke)
# 




# App-specific wrapper classes:

class EvolutionApp(Application, EmailClient):
	"""
	Useful test hooks for Evolution testcases
	"""
	def __init__(self):
		Application.__init__(self, root.application("evolution"))

		self.evoVersion = packageDb.getVersion("evolution")
		print "Evolution version %s"%self.evoVersion

		if self.evoVersion>=Version([1,5,0]):
			self.edsVersion = packageDb.getVersion("evolution-data-server")
			print "evolution-data-server version %s"%self.edsVersion
		else:
			self.edsVersion = None

		# The name of the gtkhtml package(s) for the various versions of Evolution varies between distributions:
		self.gtkhtmlVersion = None
		if distro:
			if isinstance(distro, RedHatOrFedora):
				self.gtkhtmlPackageName = "gtkhtml3"
			else:
				raise "You need to implement appropriate logic here to get the name of the gtkhtml package for your distribution for this version of Evolution"
			self.gtkhtmlVersion = packageDb.getVersion(self.gtkhtmlPackageName)
			print "%s version %s"%(self.gtkhtmlPackageName, self.gtkhtmlVersion)

	def getConfigMenuItem(self):
		"""
		Get the menu item that triggers the Settings/Preferences dialog,
		handling version-specific differences
		"""
		if self.evoVersion<Version([2,1,0]):
			return self.menu("Tools").menuItem("Settings...")
		else:
			return self.menu("Edit").menuItem("Preferences")

	def doPasswordDialog(self, password, rememberPassword):
		"""
		Utility function for dealing with Evolution's password dialog.	It
		finds the dialog, then fills in the password, setting the 'Remember
		Password' checkbox accordingly.  It then clicks on OK
		"""
		passwdDlg = self.child(roleName="alert", recursive=False, debugName="passwordDlg")
		passwdDlg.child("Remember this password").setCheckbox = rememberPassword
		passwdDlg.child(roleName="password text").passwordText = password
		passwdDlg.child("OK").click()

	def getSelectFolderDialog(self):
		"""
		Utility function to get the 'Select folder' dialog, wrapped
		"""
		return EvolutionSelectFolderDialog(self.dialog("Select folder"), self)

#FIXME: generalize this to handle arbitrary error dialogs, and allow a non-fatal version where we check that an error that was meant to occur did occur?
#FIXME: maybe allow installation of error detection hooks into the agent, and have it do it after every "action"??? (more complicated?)
	def detectAuthFailure(self):
		"""
		Detect an 'Evolution Error' dialog, raising an exception if one is
		found.	The text of the dialog is scraped into the exception.
		"""
		errorDlg = self.child("Evolution Error", recursive=False)
		if errorDlg:
			raise "AuthenticationError: %s"%errorDlg.child(roleName="label").text

#FIXME: finish the import hooks

	def __doImportFirstPage(self):
		"""
		Open the File->Import wizard and navigate to the second page
		"""
		self.menu("File").menuItem("Import...").click()
		importAssistant = Wizard(self.child("Evolution Import Assistant", recursive=False), "Import Assistant")
		importAssistant.clickForward()
		return importAssistant

	def __doImportFromOtherProgram(self):
		importAssistant = self.__doImportFirstPage()
		importAssistant.child("Import data and settings from older programs").click()
		importAssistant.clickForward()
		return importAssistant

	def __doImportFromSingleFile(self, filename, filetype):
		importAssistant = self.__doImportFirstPage()
		importAssistant.child("Import a single file").click()
		importAssistant.clickForward()

		importAssistant.child(label="Filename:").child(roleName="text").text = filename
		importAssistant.child(label="File type:").combovalue=filetype
		importAssistant.clickForward()
		
		return importAssistant
	
	def importSingleEmail(self, filename, useSubfolder=False):
		"""
		Test hook to test importing a single email.  Imports the email into a
		local folder (either the local Inbox, or creates specially-purpose
		subfolder inside the local Inbox), then views that email (and then
		tests that Evolution is still running)

		FIXME: not fully implemented yet
		"""

		# Tested on Evolution 2.0.4 and Evolution 2.4.0:
		# FIXME: what's the _exact_ value for this version test?
		if self.evoVersion>=Version([2,4.0]):
			filetype = "Berkeley Mailbox (mbox)"
		else:
			filetype = "MBox (mbox)"
	   
		importAssistant = self.__doImportFromSingleFile(filename, filetype)

		if useSubfolder:
			# Unfortunately this doesn't yet have a labelling relationship (in evolution-data-server 1.4.0)
			#importAssistant.child(label="Destination folder:").click()
			# So we get it by its label:
			importAssistant.child("Inbox").click()

			selectFolderDlg = self.getSelectFolderDialog()
			folderName = "test folder for %s"%agent.testRunId
			selectFolderDlg.newInboxSubfolder(folderName)
			# FIXME: the above can fail if the testrun ID contains characters that can't be a folder name
		
		importAssistant.clickForward()
		importAssistant.child("Import").click()

		# FIXME: now view it and see if we're still alive
		# use PrintPreview as well

	def __doIdentityPage(self, accountWiz, account):	
		# "Identity" page:
		accountWiz.child(label="Full Name:").text = account.fullName
		accountWiz.child(label="Email Address:").text = account.emailAddress
		accountWiz.child(label="Reply-To:").text = account.replyTo
		accountWiz.child(label="Organization:").text = account.organisation
		accountWiz.clickForward()

	def __doReceivingEmailPage(self, accountWiz, account):	
		# "Receiving Email" page:
		accountWiz.child(label="Server Type: ").combovalue=account.getReceivingComboValue()

		if isinstance(account, ExchangeAccount):
			if self.evoVersion>Version([2,3,0]):
				accountWiz.child(label="Username:").text = account.windowsUsername
				accountWiz.child(label="OWA Url:").text = account.urlForOWA

				# For Exchange, in Evolution 2.3 and later we have to click on the authenticate button to get further:
				accountWiz.child("Authenticate").click()
				self.doPasswordDialog(account.password, True)
				self.detectAuthFailure()
			else:
				accountWiz.child(label="Exchange Server:").text = account.server
				accountWiz.child(label="Windows Username:").text = account.windowsUsername
				
		elif isinstance(account,MixedAccount):
			# In Evolution 2.0.4, server field is labelled "Host:", in Evolution 2.4.0 it is labelled "Server:"
			# FIXME: check for other versions of Evolution; what is the _exact_ test here?
			if self.evoVersion<Version([2,4,0]):
				accountWiz.child(label="Host:").text = account.receiveMethod.server
			else:
				accountWiz.child(label="Server:").text = account.receiveMethod.server
			accountWiz.child(label="Username:").text = account.receiveMethod.username
			# FIXME: "Use secure Connection"
			# FIXME: "Check for Supported Types"
			# FIXME: "Remember password"
		else:
			raise NotImplementedError

		accountWiz.clickForward()

	def __doReceivingOptionsPage(self, accountWiz, account):	
		# "Receiving Options" page:
		# FIXME: implement
		accountWiz.clickForward()

	def __doSendingEmailPage(self, accountWiz, account):	
		# "Sending Email" page:
		# FIXME: this fails; it picks up on the "Server Type:" from the earlier page
		# and hence can't find the value it wants in the combo.  Should use the correct page for all of this...
		sendingEmailPage = accountWiz.currentPage()
		sendingEmailPage.child(label="Server Type: ").combovalue = account.getSendingComboValue()
		print sendingEmailPage
		if isinstance(account,MixedAccount):
			if isinstance(account.sendMethod,SMTPSettings):
				sendingEmailPage.child(label="Server:").text = account.sendMethod.server
				# FIXME: "Server requires authentication"
				# etc etc

				# FIXME: is this visible? "SSL is not supported in this build of Evolution"
		elif isinstance(account, ExchangeAccount):
			# Nothing should need doing
			pass
		else:
			raise NotImplementedError
		accountWiz.clickForward()

	def __doAccountManagementPage(self, accountWiz, accountName):	
		# "Account Management" page:
		accountWiz.child(label="Name:").text = accountName
		accountWiz.clickForward()

	def createAccount(self, account, accountName):
		"""
		Add a new account, running the Evolution Account Assistant, filling in
		the values given.
		"""
		
		self.getConfigMenuItem().click()
		settingsDlg = self.child("Evolution Settings", recursive=False)
		#pageTabs = settingsDlg.child(roleName="page tab list")
		# page tabs don't seem to be labelled in the tree... how do we get at this?

		# for now, assume Mail Accounts tab is selected..
		# Account wizard takes a while to appear...
		settingsDlg.child("Add").click()
		# this one needs a watch, I guess

		accountWiz = Wizard(self.child("Evolution Account Assistant", recursive=False),"Evolution Account Assistant")
		accountWiz.clickForward()

		self.__doIdentityPage(accountWiz, account)
		self.__doReceivingEmailPage(accountWiz, account)
		self.__doReceivingOptionsPage(accountWiz, account)
		self.__doSendingEmailPage(accountWiz, account)
		self.__doAccountManagementPage(accountWiz, accountName)

		# "Done" page:
		accountWiz.child("Apply").click()

		# FIXME: we should add a review stage where we check that all widgets have the correct settings.  (But why should that even be necessary? Can our framework implement that on the script's behalf? perhaps with a UITransaction class or somesuch?)

	def doFirstTimeWizard(self, account, accountName, timezoneName):
		setupWiz = Wizard(self.window('Evolution Setup Assistant'))
		setupWiz.clickForward()

		self.__doIdentityPage(setupWiz, account)
		self.__doReceivingEmailPage(setupWiz, account)
		self.__doReceivingOptionsPage(setupWiz, account)
		self.__doSendingEmailPage(setupWiz, account)
		self.__doAccountManagementPage(setupWiz, accountName)
		
		# Timezone page:
		# FIXME: timezone selection doesn't yet work
		#self.child("TimeZone Combobox").child(timezoneName).click()
		setupWiz.clickForward()

		# "Done" page:
		setupWiz.child("Apply").click()
		
	def composeEmail(self):
		"""
		Utility function to start composing a new email.

		Returns a Composer instance wrapping the new email composer window.
		"""
		self.menu("File").child("Mail Message").click()
		composer = self.window("Compose a message")
		return Composer(composer)
		
	def createMeeting(self):
		"""
		Utility function to start creating a new meeting.

		Returns a MeetingWindow instance wrapping the new meeting window.
		"""
		self.menu("File").child("Meeting").click()
		meetingWin = self.dialog("Meeting - No summary")
		return MeetingWindow(meetingWin)
		

class Composer(Window):
	"""
	Subclass of Window wrapping an Evolution email composer, with utility functions
	"""

	def __init__(self, node):
		Window.__init__(self, node)

		#FIXME: doesn't seem to be accessible on FC3 with evolution-2.0.4/gtkhtml3-3.3.2
		gtkhtmlPanel = self.child(name="Panel containing HTML", roleName="panel")
		gtkhtmlPanel.debugName="GTKHtml panel"
		self.htmlNode = gtkhtmlPanel.child(roleName="text")

	def __setattr__(self, name, value):
		if name=="to":
			# Set the To: ("addressee" if you're feeling fancy) of the email:
			self.textentry("To:").text = value
		elif name=="subject":
			# Set the subject of the email:
			self.child(label="Subject:").text = value
		elif name=="body":
			# Set the body text of the email:
			self.htmlNode.text = value
		else:
			# otherwise, use normal Python attribute-handling:
			self.__dict__[name]=value

	def setHtml(self, htmlFlag):
		if not htmlFlag:
			raise NotImplementedError
	
		# Set to HTML
		formatMenu = self.menu("Format")
		formatMenu.menuItem("HTML").click()

	def setHeader(self, level):
		"""
		Set the text type to 'Heading 1-6'
		"""
		formatMenu = self.menu("Format")
		headingMenu = formatMenu.menu("Heading")
		headingMenu.menuItem("Header %s"% level).click()

	def setBulletedList(self):
		"""
		Sets the text style to be 'Bulleted List'
		"""
		formatMenu = self.menu("Format")
		headingMenu = formatMenu.menu("Heading")
		headingMenu.menuItem("Bulleted List").click()

	def typeText(self, text):
		self.htmlNode.typeText(text)

	def send(self):
		"""
		Clicks on the Send menu item to send this email.   Use with caution!
		"""
		self.menuItem("Send").click()

	def testUndoRedo(self):
		"""
		Repeatedly does an 'Undo' until everything is undone, then does a 'Redo'
		that many times, and checks that the content is the same.

		Unfortunately, this doesn't work; Undo is always sensitive, even when
		there's nothing to undo:
		http://bugzilla.gnome.org/show_bug.cgi?id=257214
		"""
		numUndos = 0
		undo = self.menuItem("Undo")
		redo = self.menuItem("Redo")

		originalText = self.htmlNode.text
		
		while undo.sensitive:
			undo.click()
			numUndos+=1

		# Now redo it:
		for i in range(numUndos):
			redo.click()

		newText = self.htmlNode.text

		if newText!=originalText:
			raise UndoRedoException(originalText, newText)

class UndoRedoException(Exception):
	def __init__(self, originalValue, newValue):
		self.originalValue = originalValue
		self.newValue = newValue

	def __str__(self):
		return "Original value %s not equal to new value %s"%(originalValue, newValue)

class AppointmentWindow(Window):
	"""
	Subclass of Window wrapping an Evolution appointment window, with utility functions
	"""
	def __init__(self, node):
		Window.__init__(self, node)

	def __setattr__(self, name, value):
		if name=="summary":
			self.tab("Appointment").child(label="Summary:").text = value
		else:
			# otherwise, use normal Python attribute-handling:
			self.__dict__[name]=value

class MeetingWindow(AppointmentWindow):
	"""
	Subclass of AppointmentWindow wrapping an Evolution meeting window, with utility functions
	"""
	def __init__(self, node):
		AppointmentWindow.__init__(self, node)
		self.invitationsTab = self.tab("Invitations")
		self.attendeeTable = self.invitationsTab.child(roleName='table')
		
	def addAttendee(self, attendee, attendeeType, role, rsvp, status):
		"""
		Add an attendeee to this meeting.  Doesn't fully work yet.
		"""
		self.invitationsTab.button('Add').click()

class SelectFolderDialog(Window):
	"""
	Subclass of Window wrapping an Evolution 'Select Folder' dialog, with
	utility functions
	"""

	def __init__(self, node, evoApp):
		Window.__init__(self, node)
		self.evoApp = evoApp

	def newInboxSubfolder(self, name):
		self.child("New").click()
		createFolderDlg = self.evoApp.dialog("Create folder")
		createFolderDlg.child(label="Folder name:").text = name

		tree = self.child("Mail Folder Tree")
		tableCell = "On This Computer"
		"Inbox"
		# FIXME: need implement table stuff for this...
		#"On This Computer" / "Inbox"
		
		# FIXME: select parent folder
		createFolderDlg.child("Create").click()
		# this is only clickable if we have a sane folder name and a selected parent

		# FIXME: now need to select the new folder in the Select Folder dialog

		# FIXME: finally, should click on OK (or should the caller do this?)

class Account:
	"""
	Base class for an Evolution account, for use when creating test accounts
	"""
	def __init__(self, fullName, emailAddress, replyTo="", organisation="", password=""):
		self.fullName = fullName
		self.emailAddress = emailAddress
		self.replyTo = replyTo
		self.organisation = organisation
		self.password = password

	def getReceivingComboValue(self):
		raise NotImplementedError

	def getSendingComboValue(self):
		raise NotImplementedError

class UseSecureConnection:
	NEVER, WHENEVER, ALWAYS = ("NEVER", "WHENEVER", "ALWAYS")

class ExchangeAccount(Account):
	"""
	Subclass of Account representing an Exchange account
	"""
	def __init__(self, fullName, emailAddress, windowsUsername, server="", urlForOWA="", replyTo="", organisation="", password=""):
		Account.__init__(self, fullName, emailAddress, replyTo, organisation, password)
		self.windowsUsername = windowsUsername
		self.server = server
		self.urlForOWA = urlForOWA

	def getReceivingComboValue(self):
		return "Microsoft Exchange"

	def getSendingComboValue(self):
		return "Microsoft Exchange"

class MixedAccount(Account):
	"""
	Subclass of Account representing a combination of a receiving method and a
	sending method
	"""
	def __init__(self, fullName, emailAddress, receiveMethod, sendMethod, replyTo="", organisation="", ):
		Account.__init__(self, fullName, emailAddress, replyTo, organisation, password="")
		assert isinstance(receiveMethod, ReceiveSettings)
		assert isinstance(sendMethod, SendSettings)
		self.receiveMethod = receiveMethod
		self.sendMethod = sendMethod		

	def getReceivingComboValue(self):
		return self.receiveMethod.getServerTypeComboValue()

	def getSendingComboValue(self):
		return self.sendMethod.getServerTypeComboValue()

class ReceiveSettings:
	def getServerTypeComboValue(self):
		raise NotImplementedError
	
class SendSettings:
	def getServerTypeComboValue(self):
		raise NotImplementedError

class IMAPSettings(ReceiveSettings):
	def __init__(self, server, username, useSecureConnection, authenticationType, rememberPassword=False):
		self.server = server
		self.username = username
		self.useSecureConnection = useSecureConnection
		self.authenticationType = authenticationType
		self.rememberPassword = rememberPassword

	def getServerTypeComboValue(self):
		return "IMAP"

class SMTPSettings(SendSettings):
	def __init__(self, server, useSecureConnection, authenticationType="plain", requireAuth=False, username="", rememberPassword=False):
		self.server = server
		self.username = username
		self.useSecureConnection = useSecureConnection
		self.authenticationType = authenticationType
		self.rememberPassword = rememberPassword
		self.requireAuth = requireAuth

	def getServerTypeComboValue(self):
		return "SMTP"

class SendmailSettings(SendSettings):
	def getServerTypeComboValue(self):
		return "Sendmail"

class ReceiptOptions:
	"""
	Class containing the options found on the 'Receiving Email' page of the
	configuration dialogs.
	"""
	def __init__(self, autocheckOn=False, autocheckInterval=10, customConnectionCommand=None, showOnlySubscribedFolders=False, overrideNamespace=None, applyFiltersToNewInInbox=False, checkNewForJunk=False, onlyCheckForJunkInInbox=False, autosyncRemoteMailLocally=False):
		raise NotImplementedError

def TestFocus():
	focus.application("evolution")
	focus.menu("File")
	click("Import...")
	focus.application("evolution")
	focus.dialog("Evolution Import Assistant")
	click("Forward") # grrr... selects the Forward menu item, rather than the Forward button

def blowAwayEvolution():
	"""
	Helper function for testing Evolution.

	Use with caution.

	This forcibly shuts down evolution, then blows away all Evolution settings.
	(FIXME: first copy the GConf data first to ./evolution-gconf-backup.xml ???)	
	"""
	os.system ('evolution --force-shutdown')
	sleep(5)
	os.system ('gconftool-2 --recursive-unset /apps/evolution')


def doFirstTimeWizard(account, accountName, timezoneName):
	"""
	Helper function for testing Evolution.

	Use with caution.

	This forcibly shuts down evolution, then blows away all Evolution settings.
	(FIXME: first copy the GConf data first to ./evolution-gconf-backup.xml ???)

	It then runs the first time wizard with the given settings.

	Returns an EvolutionApp instance.
	"""
	blowAwayEvolution()
	
	run('evolution')
	evo = EvolutionApp()
	evo.doFirstTimeWizard(account, accountName, timezoneName)

	return evo
	
