#!/usr/bin/env python
"""
Logging facilities

Authors: Ed Rousseau <rousseau@redhat.com>, Zack Cerza <zcerza@redhat.com, David Malcolm <dmalcolm@redhat.com>
"""

__author__ = """Ed Rousseau <rousseau@redhat.com>,
Zack Cerza <zcerza@redhat.com, 
David Malcolm <dmalcolm@redhat.com>
"""
import os
import time
import datetime
from config import config

# Timestamp class for file logs
class TimeStamp:
	"""
	Generates timestamps tempfiles and log entries
	"""
	def __init__(self):
		self.now = "0"
		self.timetup = time.localtime()
	
	def zeroPad(self, int, width = 2):
		"""
		Pads an integer 'int' with zeroes, up to width 'width'.
		
		Returns a string.
		
		It will not truncate. If you call zeroPad(100, 2), '100' will be returned.
		"""
		if int < 10 ** width:
			return ("0" * (width - len(str(int))) ) + str(int)
		else: 
			return str(int)

	# file stamper
	def fileStamp(self, filename, addTime = True):
		"""
		Generates a filename stamp in the format of filename_YYYYMMDD-hhmmss.
		A format of filename_YYYYMMDD can be used instead by specifying addTime = False.
		"""
		self.now = filename.strip() + "_"
		self.timetup = time.localtime()

		# Should produce rel-eng style filestamps
		# format it all pretty by chopping the tuple
		fieldCount = 3
		if addTime: fieldCount = fieldCount + 3
		for i in range(fieldCount):
			if i == 3: self.now = self.now + '-'
			self.now = self.now + self.zeroPad(self.timetup[i])
		return self.now

	# Log entry stamper
	def entryStamp(self):
		"""
		Generates a logfile entry stamp of YYYY.MM.DD HH:MM:SS
		"""
		self.timetup = time.localtime()

		# This will return a log entry formatted string in YYYY.MM.DD  HH:MM:SS
		for i in range(6):
			# put in the year
			if i == 0:
				self.now = str(self.timetup[i])
			# Format Month and Day
			elif i == 1 or i == 2:
				self.now = self.now + "." + self.zeroPad(self.timetup[i])
			else:
				x = self.timetup[i]
				# make the " " between Day and Hour and put in the hour
				if i == 3:
					self.now = self.now + " " + self.zeroPad(self.timetup[i])
				# Otherwise Use the ":" divider
				else:
					self.now = self.now + ":" + self.zeroPad(self.timetup[i])
		return self.now


# Class that writes to the Log
class LogWriter:
	"""
	Writes entries into the Dogtail log
	"""
	def __init__(self):
		self.entry = {}
		# Set the logDir - maybe we want to use mktemp(1) for this later.
		self.logDir = config.logDir #'/tmp/dogtail-' + os.environ['LOGNAME'] + '/'
		if not os.path.isdir(self.logDir): os.makedirs(self.logDir)
		self.logfile = ''
		self.scriptName = config.scriptName 
		if not self.scriptName: self.scriptName = 'log'
		self.loghandle = "" # Handle to the logfile
		self.stamper = TimeStamp()
		# check to see if we can write to the logDir
		if os.path.isdir(self.logDir):
			# generate a logfile name and check if it already exists
			self.logfile = self.logDir + self.stamper.fileStamp(self.scriptName)
			i = 0
			while os.path.exists(self.logfile):
				# Append the pathname
				if i == 0:
					self.logfile = self.logfile + "." + str(i)
				else:
					logsplit = self.logfile.split(".")
					logsplit[-1] = str(i)
					self.logfile = ".".join(logsplit)
				i += 1
		else:
			# If path doesn't exist, raise an exception
			raise IOError, "Log path %s does not exist or is not a directory" % self.logDir

		# Try to create the file and write the header info
		try:
			print "Creating logfile at %s ..." % self.logfile
			date = datetime.datetime.strftime(datetime.datetime.now(), '%d %b %Y %H:%M:%S')
			self.loghandle = open(self.logfile, 'w')
			self.loghandle.write("##### " + self.scriptName + " Created on: " + date + "\n")
			self.loghandle.flush()
			self.loghandle.close()
		except IOError:
			print "Could not create and write to " + self.logfile


	# Writes the result of a test case comparison to the log
	def writeResult(self, entry):
		"""
		Writes the log entry. Requires a 1 {key: value} pair dict for an argument or else it will throw an exception.
		"""
		self.entry = entry
		# We require a 1 key: value dict
		# Strip all leading and trailing witespace from entry dict and convert
	# to string for writing

		if len(self.entry) == 1:
			key = self.entry.keys()
			value = self.entry.values()
			key = key[0]
			value = value[0]
			self.entry = str(key) + ":	" + str(value)
		else:
			raise ValueError
			print "Method argument requires a 1 {key: value} dict. Supplied argument not one {key: value}"

		# Try to open and write the result to the log
		try:
			self.loghandle = open(self.logfile, 'a')
			self.loghandle.write(self.stamper.entryStamp() + "	" + self.entry + "\n")
			self.loghandle.flush()
			self.loghandle.close()

		except IOError:
			print "Could not write to file " + self.logfile

class IconLogger:
	"""
	Writes entries to the tooltip of an icon in the notification area or the desktop.
	"""
	trayicon = None
	def __init__(self, config = None, module_list = None):
		if not IconLogger.trayicon:
			from trayicon import TrayIcon
			IconLogger.trayicon = TrayIcon()
			if IconLogger.trayicon.proc: self.works = True
			else: self.works = False
			iconName = 'dogtail-tail-48.png'
			iconPath = '/usr/share/icons/hicolor/48x48/apps/' + iconName
			if os.path.exists(iconPath):
				IconLogger.trayicon.set_icon(iconPath)
			self.message('dogtail running...')

	def message(self, msg):
		"""
		Display a message to the user
		"""
		IconLogger.trayicon.set_tooltip(msg)

class DebugLogger:
	"""
	Writes entries to standard out, and to an IconLogger if possible.
	"""
	def __init__(self):
		self.iconLogger = IconLogger()

	def log(self, message):
		"""
		Hook used for logging messages.  Might eventually be a virtual
		function, but nice and simple for now.
		"""
		# Try to use the IconLogger.
		if self.iconLogger.works: self.iconLogger.message(message)
		# Also write to standard out.
		print message

debugLogger = DebugLogger()
