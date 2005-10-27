#!/usr/bin/env python
"""
The configuration module.
"""
__author__ = "Zack Cerza <zcerza@redhat.com>, David Malcolm <dmalcolm@redhat.com>"

import os
import sys
import locale

def _scriptName():
	return os.path.basename(sys.argv[0]).replace('.py','')

def _encoding():
	return locale.getpreferredencoding().lower()

class _Config(object):
	"""
	Contains configuration parameters for the dogtail run.

	ensureSensitivity (boolean):
	Should we check that ui nodes are sensitive (not 'greyed out') before
	performing actions on them? If this is True (the default) it will raise
	an exception if this happens. Can set to False as a workaround for apps
	and toolkits that don't report sensitivity properly.

	searchBackoffDuration (float):
	Time in seconds for which to delay when a search fails.

	searchWarningThreshold (int):
	Number of retries before logging the individual attempts at a search.

	searchCutoffCount (int):
	Number of times to retry when a search fails.
	
	debugSearching (boolean):
	Whether to write info on search backoff and retry to the debug log.
	
	debugSleep (boolean):
	Whether to log whenever we sleep to the debug log.
	
	defaultDelay (float):
	Default time in seconds to sleep when delaying.
	
	absoluteNodePaths (boolean):
	Whether we should identify nodes in the logs with long 'abcolute paths', or
	merely with a short 'relative path'. FIXME: give examples
	
	debugSearchPaths (boolean):
	Whether we should write out debug info when running the SearchPath
	routines.
	"""
	__scriptName = staticmethod(_scriptName)
	__encoding = staticmethod(_encoding)
	
	defaults = {
		# Storage
		'scratchDir' : '/tmp/dogtail/',
		'dataDir' : '/tmp/dogtail/data/',
		'logDir' : '/tmp/dogtail/logs/',
		'scriptName' : _scriptName(),
		'encoding' : _encoding(),
		'configFile' : None,
		'baseFile' : None,
		
		# Timing
		'actionDelay' : 1.0,
		'runInterval' : 0.5,
		'runTimeout' : 30,
		'searchBackoffDuration' : 0.5,
		'searchWarningThreshold' : 3,
		'searchCutoffCount' : 20,
		'defaultDelay' : 0.5,

		# Debug
		'debugSearching' : False,
		'debugSleep' : False,
		'debugSearchPaths' : False,
		'absoluteNodePaths' : False,
		'ensureSensitivity' : True
	}
	
	options = {}
	
	invalidValue = "__INVALID__"

	def __init__(self):
		scriptName = _scriptName()
		encoding = _encoding()
		_Config.__createDir(_Config.defaults['scratchDir'])
		_Config.__createDir(_Config.defaults['logDir'])
		_Config.__createDir(_Config.defaults['dataDir'])

	def __setattr__(self, name, value):
		try:
			if _Config.defaults[name] != value or _Config.options.get(name, _Config.invalidValue) != value:
				if "Dir" in name: _Config.__createDir(value)
				_Config.options[name] = value
		except KeyError: raise KeyError, name + " is not a valid option."
	
	def __getattr__(self, name):
		try: return _Config.options[name]
		except KeyError:
			try: return _Config.defaults[name]
			except KeyError: raise KeyError, name + " is not a valid option."

	def __createDir(cls, dirName):
		"""
		Creates a directory (if it doesn't currently exist), creating any parent directories it needs.
		"""
		dirName = os.path.abspath(dirName)
		#print "Checking for %s ..." % dirName,
		if not os.path.isdir(dirName): 
			#print "Not found."
			parentDirName = os.path.sep + os.path.sep.join(os.path.split(dirName + os.path.sep)[0].split(os.path.sep)[1:-1])
			#print "Checking for parent %s ..." % parentDirName,
			if not os.path.isdir(parentDirName): 
				#print "Not found."
				#print "Parent %s ..." % parentDirName
				_Config.__createDir(parentDirName)
				print "Creating %s ..." % dirName
				os.mkdir(dirName)
			else:
				#print "Found."
				print "Creating %s ..." % dirName
				os.mkdir(dirName)
		#else: print "Found."
	__createDir = classmethod(__createDir)
	
	def load(self, dict):
		"""
		Loads values from dict, preserving any options already set that are not overridden.
		"""
		_Config.options.update(dict)
	
	def	reset(self):
		"""
		Resets all settings to their defaults.
		"""
		_Config.options = {}


config = _Config()

if __name__ == '__main__':
	anyFailed = False
	def failOrPass(failure, description):
		if failure: 
			anyFailed = True
			print "FAILED: " + description
		else: print "PASSED: " + description
	
	# BEGIN tests
	
	failure = True
	for option in config.defaults.keys():
		#print failure, getattr(config, option), config.defaults[option]
		failure = not failure and ( getattr(config, option) == config.defaults[option])
	failOrPass(failure, "Reading all default values")
	
	failure = True
	failure = config.ensureSensitivity != True
	config.ensureSensitivity = False
	failure = failure or config.ensureSensitivity == True
	config.ensureSensitivity = True
	failure = failure or config.ensureSensitivity != True
	failOrPass(failure, "Setting ensureSensitivity")

	failure = True
	failure = not os.path.isdir(config.defaults['scratchDir'])
	failure = failure or not os.path.isdir(config.defaults['logDir'])
	failure = failure or not os.path.isdir(config.defaults['dataDir'])
	failOrPass(failure, "Looking for default directories")

	failure = True
	config.scratchDir = '/tmp/dt'
	failure = not os.path.isdir('/tmp/dt')
	config.logDir = '/tmp/dt_log/'
	failure = failure or not os.path.isdir('/tmp/dt_log/')
	config.dataDir = '/tmp/dt_data'
	failure = failure or not os.path.isdir('/tmp/dt_data')
	failOrPass(failure, "Changing default directories")

	# END tests
	
	if anyFailed: sys.exit(1)
