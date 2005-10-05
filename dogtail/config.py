#!/usr/bin/env python
"""The configuration module

Author: Ed Rousseau <rousseau@redhat.com>, David Malcolm <dmalcolm@redhat.com>"""
__author__ = "Ed Rousseau <rousseau@redhat.com>, David Malcolm <dmalcolm@redhat.com>"

import os
import sys
import os.path
import locale
import string

class Config:
	"""
	Contains configuration parameters for the dogtail run.

	ensureSensitivity (boolean):
	Should we check that ui nodes are sensitive (not 'greyed out') before
	performing actions on them?  If this is True (the default) it will raise
	an exception if this happens.  Can set to False as a workaround for apps
	and toolkits that don't report sensitivity properly.

	searchBackoffDuration (float):
	Time in seconds for which to delay when a search fails.

	searchWarningThreshold (int):
	Number of retries before logging the individual attempts at a search

	searchCutoffCount (int):
	Number of times to retry when a search fails
	
	debugSearching (boolean):
	Whether to write info on search backoff and retry to the debug log
	
	debugSleep (boolean):
	Whether to log whenever we sleep to the debug log
	
	defaultDelay (float):
	Default time in seconds to sleep when delaying
	
	absoluteNodePaths (boolean):
	Whether we should identify nodes in the logs with long 'abcolute paths', or
	merely with a short 'relative path'.	FIXME: give examples
	
	debugSearchPaths (boolean):
	Whether we should write out debug info when running the SearchPath
	routines
	"""
				

	logdir = '/tmp/dogtail/logs/' # logs directory
	scratch = '/tmp/dogtail/' # temp directory
	scriptname = os.path.basename(sys.argv[0]).replace('.py','')
	encoding = locale.getpreferredencoding().lower()
	basefile = '' # baseline file to load
	data = '/tmp/dogtail/data/' # location to save screenshots and the like
	actionDelay = 1.0
	runInterval = 0.5
	runTimeout = 30
	configfile = '' # The configuration file loaded

	ensureSensitivity = True
	searchBackoffDuration = 0.5
	searchWarningThreshold = 3
	searchCutoffCount = 20
	debugSearching = False
	debugSleep = False
	defaultDelay = 0.5
	absoluteNodePaths = False
	debugSearchPaths = False

	def __init__(self, file = None):
		# Setup our default directories and values
		Config.scriptname = os.path.basename(sys.argv[0]).replace('.py','')
		Config.encoding = locale.getpreferredencoding().lower()
		
		if file: Config.load(self, file)

	# loads configuration details from file
	def load(self, filepath):
		Config.configfile = filepath
		try:
			if os.path.isfile(Config.configfile):
				cfile = open(Config.configfile, 'r').readlines()
				# Read the file and pop in the new values
				for entry in cfile:
					splitline = entry.split('=')
					key = splitline[0].strip()
					value = splitline[-1].strip()
					# If we get a blank value skip it
					if not value:
						pass
					elif Config.__dict__.has_key(key):
						# If the key is sleep convert the str to a float
						if key in ('actionDelay', 'runInterval', 'runTimeout'): key = float(key)
						Config.__dict__[key] = value
					else: raise ValueError, key

			else:
				raise IOError, "Cannot find specified configuration file" + Config.basefile

		except IOError:
			print "Failed to set up specified paths properly. Please check " + Config.basefile


##### START UNIT TEST SECTION #####

if __name__ == '__main__':
	# Config Defaults
	dlogdir = '/tmp/dogtail/logs/'
	dscratch = '/tmp/dogtail/'
	dscriptname = 'config'
	dencoding = locale.getpreferredencoding()
	dbasefile = ''
	ddata = '/tmp/dogtail/data/'

	c = Config()
	print c.logdir
	if os.path.isdir(dlogdir): 
		print "Pass"
	else: 
		print "Failed"
	
	print c.scratch
	if os.path.isdir(dscratch): 
		print "Pass"
	else: 
		print "Failed"

	print c.scriptname
	if dscriptname == c.scriptname: 
		print "Pass"
	else: 
		print "Failed"

	print c.encoding
	if dencoding == c.encoding: 
		print "Pass"
	else: 
		print "Failed"

	print c.basefile
	if dbasefile == c.basefile: 
		print "Pass"
	else: 
		print "Failed"

	print c.data
	if os.path.isdir(ddata): print "Pass"
	else: print "Failed"

	# load our values
	dlogdir = '../scratch/logs/'
	dscratch = '../scratch/'
	dscriptname = 'config-loaded'
	dencoding = 'utf-8'
	dbasefile = ''
	ddata = '../scripts/pound'

	c.load('../scripts/pound/sample.cfg')
	print "\n"
	print "Loaded values start here."
	print c.logdir
	if os.path.isdir(dlogdir):
		print "Pass"
	else:
		print "Failed"

	print c.scratch
	if os.path.isdir(dscratch):
		print "Pass"
	else:
		print "Failed"

	print c.scriptname
	if dscriptname == c.scriptname:
		print "Pass"
	else:
		print "Failed"

	print c.encoding
	if dencoding == c.encoding:
		print "Pass"
	else:
		print "Failed"

	print c.basefile
	if dbasefile == c.basefile:
		print "Pass"
	else:
		print "Failed"

	print c.data
	if os.path.isdir(ddata): print "Pass"
	else: print "Failed"

