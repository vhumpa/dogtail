"""Handles differences between different distributions

Authors: Dave Malcolm <dmalcolm@redhat.com>, Zack Cerza <zcerza@redhat.com>"""
__author__ = "Dave Malcolm <dmalcolm@redhat.com>, Zack Cerza <zcerza@redhat.com>"

import os
from version import Version


class DistributionNotSupportedError(Exception):
	"""
	This distribution is not supported.

	Arguments:
		distro: the distribution that is not supported.
	"""
	PATCH_MESSAGE = "Please send patches to dogtail-devel-list@gnome.org"

	def __init__(self, distro):
		self.distro = distro

	def __str__(self):
		return self.distro + ". " + DistributionNotSupportedError.PATCH_MESSAGE

class PackageNotFoundError(Exception):
	"""
	Error finding the requested package.
	"""
	pass

global packageDb
global distro

class PackageDb:
	"""
	Class to abstract the details of whatever software package database is in use (RPM, APT, etc)
	"""
	def __init__(self):
		self.prefix = '/usr'
		self.localePrefixes = [self.prefix + '/share/locale']

	def getVersion(self, packageName):
		"""
		Method to get the version of an installed package as a Version instance (or raise an exception if not found)
		Note: does not know about distributions' internal revision numbers.
		"""
		raise NotImplementedError

	def getFiles(self, packageName):
		"""
		Method to get a list of filenames owned by the package, or raise an exception if not found.
		"""
		raise NotImplementedError

	def getMoFiles(self, locale = None):
		"""
		Method to get a list of all .mo files on the system, optionally for a specific locale.
		"""
		moFiles = {}

		def appendIfMoFile(moFiles, dirName, fNames):
			import re
			for fName in fNames:
				if re.match('(.*)\\.mo', fName):
					moFiles[dirName + '/' + fName] = None
		
		for localePrefix in self.localePrefixes:
			if locale: localePrefix = localePrefix + '/' + locale
			os.path.walk(localePrefix, appendIfMoFile, moFiles)

		return moFiles.keys()

	def getDependencies(self, packageName):
		"""
		Method to get a list of unique package names that this package 
		is dependent on, or raise an exception if the package is not 
		found.
		"""
		raise NotImplementedError

class _RpmPackageDb(PackageDb):
	def __init__(self):
		PackageDb.__init__(self)

	def getVersion(self, packageName):
		import rpm
		ts = rpm.TransactionSet()
		for header in ts.dbMatch("name", packageName):
			return Version.fromString(header["version"])
		raise PackageNotFoundError, packageName

	def getFiles(self, packageName):
		import rpm
		ts = rpm.TransactionSet()
		for header in ts.dbMatch("name", packageName):
			return header["filenames"]
		raise PackageNotFoundError, packageName

	def getDependencies(self, packageName):
		import rpm
		ts = rpm.TransactionSet()
		for header in ts.dbMatch("name", packageName):
			# Simulate a set using a hash (to a dummy value);
			# sets were only added in Python 2.4
			result = {}

			# Get the list of requirements; these are 
			# sometimes package names, but can also be
			# so-names of libraries, and invented virtual 
			# ids
			for requirement in header[rpm.RPMTAG_REQUIRES]:
				# Get the name of the package providing
				# this requirement:
				for depPackageHeader in ts.dbMatch("provides", requirement):
					depName = depPackageHeader['name']
					if depName!=packageName:
						# Add to the Hash with a dummy value
						result[depName]=None
			return result.keys()
		raise PackageNotFoundError, packageName

class _AptPackageDb(PackageDb):
	def __init__(self):
		PackageDb.__init__(self)
		self.cache = None
	
	def getVersion(self, packageName):
		if not self.cache:
			import apt_pkg
			apt_pkg.init()
			self.cache = apt_pkg.GetCache()
		packages = self.cache.Packages
		for package in packages:
			if package.Name == packageName:
				import re
				verString = re.match('.*Ver:\'(.*)-.*\' Section:', str(package.CurrentVer)).group(1)
				return Version.fromString(verString)
		raise PackageNotFoundError, packageName

	def getFiles(self, packageName):
		files = []
		list = os.popen('dpkg -L %s' % packageName).readlines()
		if not list:
			raise PackageNotFoundError, packageName
		else:
			for line in list:
				file = line.strip()
				if file: files.append(file)
			return files
	
	def getDependencies(self, packageName):
		# Simulate a set using a hash (to a dummy value);
		# sets were only added in Python 2.4
		result = {}
		if not self.cache:
			import apt_pkg
			apt_pkg.init()
			self.cache = apt_pkg.GetCache()
		packages = self.cache.Packages
		for package in packages:
			if package.Name == packageName:
				current = package.CurrentVer
				if not current:
					raise PackageNotFoundError, packageName
				depends = current.DependsList
				list = depends['Depends']
				for dependency in list:
					name = dependency[0].TargetPkg.Name
					# Add to the hash using a dummy value
					result[name] = None
		return result.keys()

class _UbuntuAptPackageDb(_AptPackageDb):
	def __init__(self):
		_AptPackageDb.__init__(self)
		self.localePrefixes.append(self.prefix + '/share/locale-langpack')

class _PortagePackageDb(PackageDb):
	def __init__(self):
		PackageDb.__init__(self)

	def getVersion(self, packageName):
		# the portage utilities are almost always going to be in /usr/lib/portage/pym
		import sys
		sys.path.append ('/usr/lib/portage/pym')
		import portage
		# FIXME: this takes the first package returned in the list, in the case that there are
		# slotted packages, and removes the leading category such as 'sys-apps'
		gentooPackageName = portage.db["/"]["vartree"].dbapi.match(packageName)[0].split('/')[1];
		# this removes the distribution specific versioning returning only the upstream version
		upstreamVersion = portage.pkgsplit(gentooPackageName)[1]
		#print "Version of package is: " + upstreamVersion
		return Version.fromString(upstreamVersion);

class _ConaryPackageDb(PackageDb):
	def __init__(self):
		PackageDb.__init__(self)

	def getVersion(self, packageName):
		import conary
		from conaryclient import ConaryClient
		client = ConaryClient()
		dbVersions = client.db.getTroveVersionList(packageName)
		if not len(dbVersions):
			raise PackageNotFoundError, packageName
		return dbVersions[0].trailingRevision().asString().split("-")[0]

class JhBuildPackageDb(PackageDb):
	def __init__(self):
		PackageDb.__init__(self)
		prefixes = []
		prefixes.append(os.environ['LD_LIBRARY_PATH'])
		prefixes.append(os.environ['XDG_CONFIG_DIRS'])
		prefixes.append(os.environ['PKG_CONFIG_PATH'])
		self.prefix = os.path.commonprefix(prefixes)
		self.localePrefixes.append(self.prefix + '/share/locale')
	
	def getDependencies(self, packageName):
		result = {}
		lines = os.popen('jhbuild list ' + packageName).readlines()
		for line in lines:
			if line:
				result[line.strip()] = None
		return result.keys()

class Distro:
	"""
	Class representing a distribution.
	
	Scripts may want to do arbitrary logic based on whichever distro is in use (e.g. handling differences in names of packages, distribution-specific patches, etc.)

	We can either create methods in the Distro class to handle these, or we can use constructs like isinstance(distro, Ubuntu) to handle this. We can even create hierarchies of distro subclasses to handle this kind of thing (could get messy fast though)
	"""

class RedHatOrFedora(Distro):
	"""
	Class representing one of Red Hat Linux, Fedora, Red Hat Enterprise Linux, or one of the rebuild-style derivatives
	"""
	def __init__(self):
		self.packageDb = _RpmPackageDb()

class Debian(Distro):
	"""
	Class representing one of the Debian or Debian-derived distributions
	"""
	def __init__(self):
		self.packageDb = _AptPackageDb()

class Ubuntu(Debian):
	"""
	Class representing one of the Debian or Debian-derived distributions
	"""
	def __init__(self):
		self.packageDb = _UbuntuAptPackageDb()

class Suse(Distro):
	"""
	Class representing one of the SuSE or SuSE-derived distributions
	"""

class Gentoo(Distro):
	"""
	Class representing one of the Gentoo or Gentoo-derived distributions
	"""
	def __init__(self):
		self.packageDb = _PortagePackageDb()

class Conary(Distro):
	"""
	Class representing a Conary-based distribution
	"""
	def __init__(self):
		self.packageDb = _ConaryPackageDb()

class JHBuild(Distro):
	"""
	Class representing a JHBuild environment
	"""
	def __init__(self):
		self.packageDb = JhBuildPackageDb()

print "Detecting distribution:",
if os.environ.get("CERTIFIED_GNOMIE", "no") == "yes":
	print "JHBuild environment"
	distro = JHBuild()
elif os.path.exists ("/etc/redhat-release"):
	print "Red Hat/Fedora/derived distribution"
	distro = RedHatOrFedora()
elif os.path.exists ("/etc/SuSE-release"):
	print "SuSE (or derived distribution)"
elif os.path.exists ("/etc/fedora-release"): 
	print "Fedora (or derived distribution)"
	distro = RedHatOrFedora()
elif os.path.exists ("/usr/share/doc/ubuntu-minimal"):
	print "Ubuntu (or derived distribution)"
	distro = Ubuntu()
elif os.path.exists ("/etc/debian_version"):
	print "Debian (or derived distribution)"
	distro = Debian()
elif os.path.exists ("/etc/gentoo-release"):
	print "Gentoo (or derived distribution)"
	distro = Gentoo()
elif os.path.exists ("/etc/slackware-version"):
	print "Slackware"
	raise DistributionNotSupportedError("Slackware")
elif os.path.exists ("/var/lib/conarydb/conarydb"):
	print "Conary-based distribution"
	distro = Conary()
else:
	print "Unknown"
	raise DistributionNotSupportedError("Unknown")

packageDb = distro.packageDb
