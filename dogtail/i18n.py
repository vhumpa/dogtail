#!/usr/bin/env python
"""
Internationalization facilities

Authors: David Malcolm <dmalcolm@redhat.com>
"""

__author__ = """David Malcolm <dmalcolm@redhat.com>"""

import distro
import config

import re
import gettext

from logging import debugLogger as logger

"""
Singleton list of TranslationDb instances, to be initialized by the script with 
whatever translation databases it wants.
"""
translationDbs = []

class TranslationDb:
	"""
	Abstract base class representing a database of translations
	"""
	def getTranslationsOf(self, srcName):
		"""
		Pure virtual method to look up the translation of a string.
		Returns a list of candidate strings (the translation), empty if not found.
		
		Note that a source string can map to multiple translated strings.  For 
		example, in the French translation of Evolution, the string "Forward" can 
		translate to both
		(i) "Faire suivre" for forwarding an email, and 
		(ii) "Suivant" for the next page in a wizard.
		"""
		raise NotImplementedError

class GettextTranslationDb(TranslationDb):
	"""
	Implementation of TranslationDb which leverages gettext, using a single
	translation domain.
	"""
	def __init__(self, domainName):
		self.domainName = domainName

	def getTranslationsOf(self, srcName):
		# print "searching for translations of %s"%srcName
		# Use a dict to get uniqueness:
		results = {}
		result = gettext.dgettext(self.domainName, srcName)
		#print "result in domain %s is %s"%(self.domainName, result)
		if result!=srcName:
			results[result]=None

		# Hack alert:
		#
		# Note that typical UI definition in GTK etc contains strings with 
		# underscores to denote accelerators. 
		# For example, the stock GTK "Add" item has text "_Add" which e.g. 
		# translates to "A_jouter" in French
		#
		# Since these underscores have been stripped out before we see these strings,
		# we are looking for a translation of "Add" into "Ajouter" in this case, so
		# we need to fake it, by looking up the string multiple times, with underscores
		# inserted in all possible positions, stripping underscores out of the result.  
		# Ugly, but it works.
			
		for index in range(len(srcName)):
			candidate = srcName[:index]+"_"+srcName[index:]
			result = gettext.dgettext(self.domainName, candidate)
			# print "result in domain %s for %s is %s"%(self.domainName, candidate, result)
			if result!=candidate:
				# Strip out the underscore, and add to the result:
				results[result.replace('_','')]=True
			
		return results.keys()

def translate(srcString):
	"""
	Look up srcString in the various translation databases (if any), returning
	a list of all matches found (potentially the empty list)
	"""
	# Use a dict to get uniqueness:
	results = {}
	# Try to translate the string:
	for translationDb in translationDbs:
		for result in translationDb.getTranslationsOf(srcString):
			results[result]=True

	# No translations found:
	if len(results)==0:
		if config.config.debugTranslation:
			logger.log('Translation not found for "%s"'%srcString)
	return results.keys()
		
class TranslatableString:
	"""
	Class representing a string that we want to match strings against, handling 
	translation for us, by looking it up once at construction time.
	"""  

	def __init__(self, untranslatedString):
		"""
		Constructor looks up the string in all of the translation databases, storing
		the various translations it finds.
		"""
		self.untranslatedString = untranslatedString
		self.translatedStrings = translate(untranslatedString)

	def matchedBy(self, string):
		"""
		Compare the test string against either the translation of the original 
		string (or simply the original string, if no translation was found).
		"""
		#print "comparing %s against %s"%(string, self)
		if len(self.translatedStrings)>0:
			return string in self.translatedStrings
		else:
			return string==self.untranslatedString
			
	def __str__(self):
		"""
		Provide a meaningful debug version of the string (and the translation in 
		use)
		"""
		if len(self.translatedStrings)>0:
			# build an output string, with commas in the correct places
			translations = ""			
			for i in range(len(self.translatedStrings)-1):
				translations += '"%s", '%self.translatedStrings[i]
			translations += '"%s"'%self.translatedStrings[-1]
			return '"%s" (%s)'%(self.untranslatedString, translations)
		else:
			return '"%s"'%(self.untranslatedString)



def isMoFile(filename):
	"""
	Does the given filename look like a gettext mo file?
	"""
	return re.match('(.*)\\.mo', filename)

def getMoFilesForPackage(packageName, getDependencies=True):
	"""
	Look up the named package and find all gettext mo files within it (and its 
	dependencies)
	"""
	result = []
	for filename in distro.packageDb.getFiles(packageName):
		if isMoFile(filename):
			result.append(filename)

	if getDependencies:
		# Recurse:
		for dep in distro.packageDb.getDependencies(packageName):
			# We pass False to the inner call because getDependencies has already 
			# walked the full tree
			result.extend(getMoFilesForPackage(dep, False))
		
	return result

def getTranslationDomainsForPackage(packageName, getDependencies=True):
	"""
	Return a list of translation domain names for the named package, based upon 
	all mo files provided by the package (and all its dependencies, if this is 
	true)
	"""
	# fake a set using a hash to dummy values:
	result = {}
	for filename in getMoFilesForPackage(packageName, getDependencies):
		# We assume they're of the format:
		# /usr/share/locale/name-of-locale/LC_MESSAGES/filename.mo
		m = re.match('/usr/share/locale(.*)/([a-zA-Z@_\.0-9]*)/LC_MESSAGES/(.*)\\.mo', filename)
		if m:
			# Insert the translation domain into the hash:
				result[m.group(3)]=None
		else:
			# somehow the initial regex is letting this file through:
			# /etc/pango/i386-redhat-linux-gnu/pango.modules
			pass # raise filename
	# Convert the hash to a list, containing unique entries:
	return result.keys()


def loadTranslationsFromPackageMoFiles(packageName, getDependencies=True):
	"""
	Helper function which appends all of the gettext translation domains used by 
	the package (and its dependencies) to the translation database list.
	"""
	# Keep a list of domains that are already in use to avoid duplicates.
	# The list also acts as a blacklist. For example, searching the popt
	# domain for translations makes gettext bail out, so we ignore it here.
	domains = ['popt']
	def load(packageName, getDependencies = True):
		for domainName in getTranslationDomainsForPackage(packageName, getDependencies):
			if domainName not in domains:
				#if config.config.debugTranslation:
				#	logger.log('Using translation domain "%s"'%domainName)
				translationDbs.append(GettextTranslationDb(domainName))
				domains.append(domainName)
				
	# Hack alert:
	#
	# The following special-case is necessary for Ubuntu, since their 
	# translations are shipped in a single huge package. The downside to
	# this special case, aside from the simple fact that there is one, 
	# is that it makes automatic translations much slower.

	if isinstance(distro.distro, distro.Ubuntu):
		import os
		load('language-pack-gnome-%s' % os.environ['LANG'][0:2])
	load(packageName, getDependencies)

