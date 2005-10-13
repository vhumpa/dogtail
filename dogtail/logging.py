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
from config import Config

# Timestamp class for file logs
class TimeStamp:
	"""
	Generates timestamps tempfiles and log entries
	"""
	def __init__(self):
		self.now = "0"
		self.timetup = time.localtime()
	
	def zeroPad(self, int, width = 1):
		"""
		Pads an integer 'int' with zeroes, up to width 'width'.
		Returns a string.
		"""
		if int < 10 ** width:
			return ("0" * width) + str(int)
		else: 
			return str(int)

	# file stamper
	def fileStamp(self, filename):
		"""
		Generates a temp filename of YYYYMMDD. If the file already exists, it appends a .0 and will increment by 1 until there is a unique name
		"""
		self.now = filename.strip() + "-"
		self.timetup = time.localtime()

		# Should produce rel-eng style filestamps
		# format it all pretty by chopping the tuple
		for i in range(3):
			self.now = self.now + self.zeroPad(self.timetup[i])
		return self.now

	# Log entry stamper
	def entryStamp(self):
		"""
		Generates a logfile entry stamp of YYYYMMDD HH:MM:SS
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
		# Set the logdir - maybe we want to use mktemp(1) for this later.
		self.logdir = Config.logdir #'/tmp/dogtail-' + os.environ['LOGNAME'] + '/'
		if not os.path.isdir(self.logdir): os.makedirs(self.logdir)
		self.logfile = ''
		self.scriptname = Config.scriptname 
		if not self.scriptname: self.scriptname = 'log'
		self.loghandle = "" # Handle to the logfile
		self.stamper = TimeStamp()
		# check to see if we can write to the logdir
		if os.path.isdir(self.logdir):
			# generate a logfile name and check if it already exists
			self.logfile = self.logdir + self.stamper.fileStamp(self.scriptname)
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
			raise IOError, "Log path %s does not exist or is not a directory" % self.logdir

		# Try to create the file and write the header info
		try:
			date = datetime.datetime.strftime(datetime.datetime.now(), '%d %b %Y %H:%M:%S')
			self.loghandle = open(self.logfile, 'w')
			self.loghandle.write("##### " + self.scriptname + " Created on: " + date + "\n")
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
	def __init__(self, config = None, module_list = None):
		from trayicon import TrayIcon
		self.trayicon = TrayIcon()
		if self.trayicon.proc: self.works = True
		else: self.works = False
		self.message('dogtail running...')

	def message(self, msg, module_num=-1):
		'''Display a message to the user'''
		
		#if is_xterm:
		#		 print '\033]0;dogtail: %s\007' % (msg)
		self.trayicon.set_tooltip('%s' % (msg))

	def set_action(self, action, module, module_num=-1, action_target=None):
		if module_num == -1:
			module_num = self.module_num
		if not action_target:
			action_target = module.name
		self.message('%s %s' % (action, action_target), module_num)

	def execute(self, command, hint=None):
		'''executes a command, and returns the error code'''
		if isinstance(command, (str, unicode)):
			print command
		else:
			print ' '.join(command)

		# get rid of hint if pretty printing is disabled.
		if not self.config.pretty_print: hint = None
		if hint == 'cvs':
			stdout = subprocess.PIPE
			stderr = subprocess.STDOUT
		else:
			stdout = stderr = None

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
