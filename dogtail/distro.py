"""Handles differences between different distributions

Authors: Dave Malcolm <dmalcolm@redhat.com>, Zack Cerza <zcerza@redhat.com>"""
__author__ = "Dave Malcolm <dmalcolm@redhat.com>, Zack Cerza <zcerza@redhat.com>"

import os
from version import Version

global packageDb
global distro

class PackageDb:
	"""
	Class to abstract the details of whatever software package database is in use (RPM, APT, etc)
	"""
	def getVersion(self, packageName):
		"""
		Method to get the version of an installed package as a Version instance (or raise an exception if not found)
		Note: does not know about distributions' internal revision numbers.
		"""
		raise NotImplemented

class Distro:
	"""
	Class representing a distribution.
	
	Scripts may want to do arbitrary logic based on whichever distro is in use (e.g. handling differences in names of packages, distribution-specific patches, etc.)

	We can either create methods in the Distro class to handle these, or we can use constructs like isinstance(distro, Ubuntu) to handle this.  We can even create hierarchies of distro subclasses to handle this kind of thing (could get messy fast though)
	"""

class RedHatOrFedora(Distro):
	"""
	Class representing one of Red Hat Linux, Fedora, Red Hat Enterprise Linux, or one of the rebuild-style derivatives
	"""

class Debian(Distro):
	"""
	Class representing one of the Debian or Debian-derived distributions
	"""

class Suse(Distro):
	"""
	Class representing one of the SuSE or SuSE-derived distributions
	"""

def __makeRpmPackageDb():
	"""
	Manufacture a PackageDb for an RPM system.  We hide this inside a factory method so that we only import the RPM Python bindings if we're on a platform likely to have them
	"""
	class RpmPackageDb(PackageDb):
		def getVersion(self, packageName):
			import rpm
			ts = rpm.TransactionSet()
			for header in ts.dbMatch("name", packageName):
				return Version.fromString(header["version"])
			raise "Package not found: %s"%packageName
	return RpmPackageDb()

PATCH_MESSAGE = "Please send patches to the mailing list." # FIXME: add mailing list address

def __makeAptPackageDb():
	"""
	Manufacture a PackageDb for an APT system: Debian/Ubuntu/etc.
	"""
	class AptPackageDb(PackageDb):
			def getVersion(self, packageName):
				import apt_pkg
				apt_pkg.init()
				cache = apt_pkg.GetCache()
				packages = cache.Packages
				for package in packages:
					if package.Name == packageName:
						import re
						verString = re.match('.*Ver:\'(.*)-.*\' Section:', str(package.CurrentVer)).group(1)
						return Version.fromString(verString)
				raise "Package not found: %s"%packageName
	return AptPackageDb()

print "Detecting distribution: ",
if os.path.exists ("/etc/redhat-release"):
	print "Red Hat/Fedora/derived distribution"
	distro = RedHatOrFedora()
	packageDb = __makeRpmPackageDb()
elif os.path.exists ("/etc/SuSE-release"):
	print "SuSE (or derived distribution)"
	packageDb = __makeRpmPackageDb()
elif os.path.exists ("/etc/fedora-release"): 
	print "Fedora (or derived distribution)"
	distro = RedHatOrFedora()
	packageDb = __makeRpmPackageDb()
elif os.path.exists ("/etc/debian_version"):
	print "Debian (or derived distribution)"
	distro = Debian()
	packageDb = __makeAptPackageDb()
elif os.path.exists ("/etc/gentoo-release"):
	print "Gentoo (or derived distribution)"
	raise "Gentoo support not yet implemented.	" + PATCH_MESSAGE
elif os.path.exists ("/etc/slackware-version"):
	print "Slackware"
	raise "Slackware support not yet implemented.  " + PATCH_MESSAGE
else:
	print "Unrecognised"
	raise "Your distribution was not recognised.  " + PATCH_MESSAGE
