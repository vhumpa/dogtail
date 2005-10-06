#!/usr/bin/env python
"""
Various utilities

Authors: Ed Rousseau <rousseau@redhat.com>, Zack Cerza <zcerza@redhat.com, David Malcolm <dmalcolm@redhat.com>
"""

__author__ = """Ed Rousseau <rousseau@redhat.com>,
Zack Cerza <zcerza@redhat.com, 
David Malcolm <dmalcolm@redhat.com>
"""

import os
from config import Config
from time import sleep
from logging import debugLogger as logger

def screenshot(windowname='', file='', args=''):
	"""
	This function wraps the ImageMagick import command. It is not very useful for anything except the root window right now.
	"""
	if windowname == '':
		windowname = "root"

	if file == '':
		# generate a filename 
		if os.path.isdir(Config.scratch):
			file = "screenshot.png"
			path = Config.scratch + file
			i = 1
			while os.path.exists(path):
				# Append the filename
				filesplit = file.split(".")
				filesplit[0] = filesplit[0] + str(i)
				file = ".".join(filesplit)
				path = Config.scratch + file
				i += 1
		else:
			# If path doesn't exist raise an exception
			raise IOError
			print "Specified filepath does not exist or is not a directory"

	# Generate the command and redirect STDERR to STDOUT
	# This really needs window manipulation and pyspi state binding to be done
	# to actually be really useful
	answer = []
	cmd = "import -window '" + windowname + "' " + Config.scratch + '/' + file + " " + args + " 2>&1"
	answer = os.popen(cmd).readlines()

	# If successful we should get nothing back. If not something went wrong
	# and our mouse is now probably unusable
	if answer:
		raise ValueError, "Screenshot failed: " + answer[-1]
	else: logger.log("Screenshot taken: " + path)

def run(string, timeout=Config.runTimeout, interval=Config.runInterval, desktop=None, dumb=False, appName=None):
	"""
	Runs an application. [For simple command execution such as 'rm *', use os.popen() or os.system()]
	If dumb is omitted or is False, polls at interval seconds until the application is finished starting, or until timeout is reached.
	If dumb is True, returns when timeout is reached.
	"""
	from os import environ, spawnvpe, P_NOWAIT
	if not desktop: from tree import root as desktop
	args = string.split()
	name = args[0]
	pid = spawnvpe (P_NOWAIT, name, args, environ)

	if appName==None:
		appName=args[0]
	
	if dumb:
		# We're starting a non-AT-SPI-aware application. Disable startup detection.
		sleep(timeout)
	else:
		# Startup detection code
		# The timing here is not totally precise, but it's good enough for now.
		time = 0
		while time < timeout:
			time = time + interval
			try:
				for child in desktop.children[::-1]:
					if child.name == appName:
						for grandchild in child.children:
							if grandchild.roleName == 'frame':
								from procedural import focus
								focus.application.node = child
								sleep(interval)
								return pid
			except AttributeError: pass
			sleep(interval)
	return pid

def doDelay(delay=None):
	"""
	Utility function to insert a delay (with logging and a configurable
	default delay)
	"""
	if delay is None:
		delay = Config.defaultDelay
	if Config.debugSleep:
		logger.log("sleeping for %f"%delay)
	sleep(delay)

