#!/usr/bin/python3
"""
Handles differences between different distributions.
"""

# pylint: disable=line-too-long
# ruff: noqa: E501

import os
import re
from subprocess import check_output, STDOUT
from dogtail.version import Version

from dogtail.logging import logging_class
LOGGING = logging_class.logger


__author__ = """
Dave Malcolm <dmalcolm@redhat.com>,
Zack Cerza <zcerza@redhat.com>
"""


class DistributionNotSupportedError(Exception):  # pragma: no cover
    """
    This distribution is not supported.
    """

    PATCH_MESSAGE = "Please open merge requests at https://gitlab.com/dogtail/dogtail"

    def __init__(self, distribution):
        self.distribution = distribution

    def __str__(self):
        return self.distribution + ". " + DistributionNotSupportedError.PATCH_MESSAGE


class PackageNotFoundError(Exception):
    """
    Error finding the requested package.
    """


class PackageDb:
    """
    Class to abstract the details of whatever software package database is in
    use (RPM, APT, etc)
    """

    def __init__(self):
        self.prefix = "/usr"
        self.locale_prefixes = [self.prefix + "/share/locale"]


    def get_version(self, package_name):
        """
        Method to get the version of an installed package as a Version
        instance (or raise an exception if not found)

        Note: does not know about distributions' internal revision numbers.
        """

        raise NotImplementedError


    def get_files(self, package_name):
        """
        Method to get a list of filenames owned by the package, or raise an
        exception if not found.
        """

        raise NotImplementedError


    def get_mo_files(self, locale=None):
        """
        Method to get a list of all .mo files on the system, optionally for a
        specific locale.
        """

        LOGGING.debug(f"get_mo_files(self, locale={str(locale)})")

        mo_files = {}

        def append_if_mo_file(mo_files, dir_name, f_names):
            for f_name in f_names:
                if re.match("(.*)\\.mo", f_name):
                    mo_files[dir_name + "/" + f_name] = None

        for locale_prefix in self.locale_prefixes:
            if locale:
                locale_prefix = locale_prefix + "/" + locale
            os.walk(locale_prefix, append_if_mo_file, mo_files)

        return list(mo_files.keys())

    def get_dependencies(self, package_name):
        """
        Method to get a list of unique package names that this package
        is dependent on, or raise an exception if the package is not
        found.
        """

        raise NotImplementedError

    ### Backwards compatibility.

    @property
    def localePrefixes(self):  # pylint: disable=invalid-name
        """
        Set localePrefixes. Wrapper over locale_prefixes.
        """
        return self.locale_prefixes


    @localePrefixes.setter
    def localePrefixes(self, value_to_set):  # pylint: disable=invalid-name
        self.locale_prefixes = value_to_set


    def getVersion(self, packageName):  # pylint: disable=invalid-name
        """
        Method to get the version of an installed package as a Version
        instance (or raise an exception if not found). Wrapper over get_version.

        Note: does not know about distributions' internal revision numbers.
        """
        return self.get_version(package_name=packageName)


    def getFiles(self, packageName):  # pylint: disable=invalid-name
        """
        Method to get a list of filenames owned by the package, or raise an
        exception if not found. Wrapper over get_files.
        """
        return self.get_files(package_name=packageName)


    def getMoFiles(self, locale=None):  # pylint: disable=invalid-name
        """
        Method to get a list of all .mo files on the system, optionally for a
        specific locale. Wrapper over get_mo_files.
        """
        return self.get_mo_files(locale=locale)


    def getDependencies(self, packageName):  # pylint: disable=invalid-name
        """
        Method to get a list of unique package names that this package
        is dependent on, or raise an exception if the package is not
        found. Wrapper over get_dependencies.
        """
        return self.get_dependencies(package_name=packageName)


class _RpmPackageDb(PackageDb):
    """
    RPM Package Database Implementation.
    """

    def get_version(self, package_name):
        import rpm   # pylint: disable=import-outside-toplevel,import-error
        transaction_set = rpm.TransactionSet()
        for header in transaction_set.dbMatch("name", package_name):
            return Version.from_string(header["version"])

        raise PackageNotFoundError(package_name)


    def get_files(self, package_name):
        import rpm   # pylint: disable=import-outside-toplevel,import-error
        transaction_set = rpm.TransactionSet()
        for header in transaction_set.dbMatch("name", package_name):
            return header["filenames"]

        raise PackageNotFoundError(package_name)


    def get_dependencies(self, package_name):
        import rpm   # pylint: disable=import-outside-toplevel,import-error
        transaction_set = rpm.TransactionSet()
        for header in transaction_set.dbMatch("name", package_name):
            result = {}

            for requirement in header[rpm.RPMTAG_REQUIRES]:
                for dependency_package_header in transaction_set.dbMatch("provides", requirement):
                    dependency_name = dependency_package_header["name"]
                    if dependency_name != package_name:

                        result[dependency_name] = None

            return list(result.keys())

        raise PackageNotFoundError(package_name)

    ### Backwards compatibility.

    def getVersion(self, packageName):
        return self.get_version(package_name=packageName)


    def getFiles(self, packageName):
        return self.get_files(package_name=packageName)


    def getDependencies(self, packageName):
        return self.get_dependencies(package_name=packageName)


class _AptPackageDb(PackageDb):
    """
    Apt Package Database Implementation.
    """

    def __init__(self):
        super().__init__()
        self.cache = None


    def get_version(self, package_name):
        if not self.cache:
            import apt_pkg  # pylint: disable=import-outside-toplevel,import-error
            apt_pkg.init()
            self.cache = apt_pkg.Cache()

        packages = self.cache.packages
        for package in packages:
            if package.name == package_name:
                version_string = re.match(".*Ver:'(.*)-.*' Section:", str(package.current_ver)).group(1)
                return Version.fromString(version_string)

        raise PackageNotFoundError(package_name)


    def get_files(self, package_name):
        files = []
        lines = os.popen(f"dpkg -L {package_name}").readlines()
        if not lines:
            raise PackageNotFoundError(package_name)

        for line in lines:
            file = line.strip()
            if file:
                files.append(file)

        return files


    def get_dependencies(self, package_name):
        result = {}
        if not self.cache:
            import apt_pkg  # pylint: disable=import-outside-toplevel,import-error
            apt_pkg.init()
            self.cache = apt_pkg.Cache()


        packages = self.cache.packages
        for package in packages:
            if package.name == package_name:
                current = package.current_ver
                if not current:
                    raise PackageNotFoundError(package_name)

                depends = current.depends_list
                dependency_list = depends["Depends"]
                for dependency in dependency_list:
                    name = dependency[0].target_pkg.name
                    result[name] = None

        return list(result.keys())

    ### Backwards compatibility.

    def getVersion(self, packageName):
        return self.get_version(package_name=packageName)


    def getFiles(self, packageName):
        return self.get_files(package_name=packageName)


    def getDependencies(self, packageName):
        return self.get_dependencies(package_name=packageName)


class _UbuntuAptPackageDb(_AptPackageDb):
    """
    Ubuntu Apt Package Database Implementation.
    """

    def __init__(self):
        _AptPackageDb.__init__(self)
        self.localePrefixes.append(self.prefix + "/share/locale-langpack")



class _PortagePackageDb(PackageDb):
    """
    Portage Package Database Implementation.
    """


    def get_version(self, package_name):
        # The portage utilities are almost always going to be in /usr/lib/portage/pym
        import sys  # pylint: disable=import-outside-toplevel
        sys.path.append("/usr/lib/portage/pym")

        import portage  # pylint: disable=import-outside-toplevel,import-error
        # This takes the first package returned in the list, in the
        # case that there are slotted packages, and removes the leading
        # category such as 'sys-apps'.
        gentoo_package_name = portage.db["/"]["vartree"].dbapi.match(package_name)[0].split("/")[1]

        # This removes the distribution specific versioning returning only the
        # upstream version.
        upstream_version = portage.pkgsplit(gentoo_package_name)[1]

        # print("Version of package is: " + upstream_version)
        return Version.fromString(upstream_version)


    ### Backwards compatibility.

    def getVersion(self, packageName):
        return self.get_version(package_name=packageName)


class _ConaryPackageDb(PackageDb):
    """
    Conary Package Database Implementation.
    """

    def get_version(self, package_name):
        from conaryclient import ConaryClient  # pylint: disable=import-outside-toplevel,import-error
        client = ConaryClient()
        database_versions = client.db.getTroveVersionList(package_name)
        if not database_versions:
            raise PackageNotFoundError(package_name)

        return database_versions[0].trailingRevision().asString().split("-")[0]

    ### Backwards compatibility.

    def getVersion(self, packageName):
        return self.get_version(package_name=packageName)


class _SolarisPackageDb(PackageDb):
    """
    Solaris Package Database Implementation.
    """

    # The getVersion not implemented because on Solaris multiple modules are installed
    # in single packages, so it is hard to tell what version number of a specific
    # module.


class JhBuildPackageDb(PackageDb):
    """
    JH Build Package Database Implementation.
    """

    def __init__(self):
        PackageDb.__init__(self)
        prefixes = []
        prefixes.append(os.environ["LD_LIBRARY_PATH"])
        prefixes.append(os.environ["XDG_CONFIG_DIRS"])
        prefixes.append(os.environ["PKG_CONFIG_PATH"])
        self.prefix = os.path.commonprefix(prefixes)
        self.locale_prefixes.append(self.prefix + "/share/locale")


    def get_dependencies(self, package_name):
        LOGGING.debug(f"get_dependencies(self, package_name={str(package_name)})")

        result = {}
        lines = os.popen("jhbuild list " + package_name).readlines()
        for line in lines:
            if line:
                result[line.strip()] = None

        return list(result.keys())


    ### Backwards compatibility.

    def getDependencies(self, packageName):
        return self.get_dependencies(package_name=packageName)



class _ContinuousPackageDb(PackageDb):
    """
    Continuous Package Database Implementation.
    """

    def get_version(self, package_name):
        return ""


    def get_files(self, package_name):
        return check_output(
            [f"ls -1 /usr/share/locale/*/LC_MESSAGES/{package_name}.mo"],
            shell=True
        ).strip().split("\n")


    def get_dependencies(self, package_name):
        return []


    ### Backwards compatibility.

    def getVersion(self, packageName):
        return self.get_version(package_name=packageName)


    def getFiles(self, packageName):
        return self.get_files(package_name=packageName)


    def getDependencies(self, packageName):
        return self.get_dependencies(package_name=packageName)


class _ArchPackageDb(PackageDb):
    """
    Arch Package Database Implementation.
    """

    def _pacman(self, option, packageName):  # pylint: disable=invalid-name
        package_name = packageName

        if option == "v":
            command_option = "i %s | grep Version | cut -d: -f2-"

        elif option == "f":
            command_option = "l %s | cut -d' ' -f2-"

        elif option == "d":
            command_option = "i %s | grep 'Depends On' | cut -d: -f2-"

        else:
            command_option = ""

        command = "LC_ALL=C COLUMNS=1000 pacman -Q" + command_option
        out = check_output(command % package_name,
                           stderr=STDOUT,
                           shell=True
                           ).decode("UTF-8")

        if out.startswith("error:"):
            raise PackageNotFoundError(package_name)

        return out.strip()


    def get_version(self, package_name):
        version = self._pacman("v", package_name)
        return Version.from_string(version)


    def get_files(self, package_name):
        files = self._pacman("f", package_name)
        return [f for f in files.split() if not f.endswith('/')]


    def get_dependencies(self, package_name):
        deps = self._pacman("d", package_name)
        return [d for d in deps.split() if d != "None"]

    ### Backwards compatibility.

    def getVersion(self, packageName):
        return self.get_version(package_name=packageName)


    def getFiles(self, packageName):
        return self.get_files(package_name=packageName)


    def getDependencies(self, packageName):
        return self.get_dependencies(package_name=packageName)


class Distro:
    """
    Class representing a distribution.

    Scripts may want to do arbitrary logic based on whichever distro is in use
    (e.g. handling differences in names of packages, distribution-specific
    patches, etc.)

    We can either create methods in the Distro class to handle these, or we
    can use constructs like isinstance(distro, Ubuntu) to handle this. We can
    even create hierarchies of distro subclasses to handle this kind of thing
    (could get messy fast though)
    """

    package_database = None

    @property
    def packageDb(self):  # pylint: disable=invalid-name
        """
        Set localePrefixes. Wrapper over locale_prefixes.
        """
        return self.package_database

    @packageDb.setter
    def packageDb(self, value_to_set):  # pylint: disable=invalid-name
        self.package_database = value_to_set


class Fedora(Distro):
    """
    Defining Fedora Distribution.
    """
    def __init__(self):
        self.package_database = _RpmPackageDb()


class RHEL(Fedora):
    """
    Defining RHEL Distribution.
    """


class Debian(Distro):
    """
    Defining Debian Distribution.
    """
    def __init__(self):
        self.package_database = _AptPackageDb()


class Ubuntu(Debian):
    """
    Defining Ubuntu Distribution based on Debian.
    """
    def __init__(self):
        super().__init__()
        self.package_database = _UbuntuAptPackageDb()


class Suse(Distro):  # pragma: no cover
    """
    Defining Suse Distribution.
    """
    def __init__(self):
        self.package_database = _RpmPackageDb()


class Gentoo(Distro):  # pragma: no cover
    """
    Defining Gentoo Distribution.
    """
    def __init__(self):
        self.package_database = _PortagePackageDb()


class Conary(Distro):  # pragma: no cover
    """
    Defining Conary Distribution.
    """
    def __init__(self):
        self.package_database = _ConaryPackageDb()


class Solaris(Distro):  # pragma: no cover
    """
    Defining Solaris Distribution.
    """
    def __init__(self):
        self.package_database = _SolarisPackageDb()


class JHBuild(Distro):  # pragma: no cover
    """
    Defining JHBuild Distribution.
    """
    def __init__(self):
        self.package_database = JhBuildPackageDb()


class GnomeContinuous(Distro):  # pragma: no cover
    """
    Defining GnomeContinuous Distribution.
    """
    def __init__(self):
        self.package_database = _ContinuousPackageDb()


class Arch(Distro):  # pragma: no cover
    """
    Defining Arch Distribution.
    """
    def __init__(self):
        self.package_database = _ArchPackageDb()


def detect_distribution():
    """
    Detect Distribution.
    """

    if os.environ.get("CERTIFIED_GNOMIE", "no") == "yes":
        distribution_detection = JHBuild()

    elif os.path.exists("/etc/SuSE-release"):
        distribution_detection = Suse()

    elif os.path.exists("/etc/fedora-release"):
        distribution_detection = Fedora()

    elif os.path.exists("/etc/redhat-release"):
        distribution_detection = RHEL()

    elif os.path.exists("/usr/share/doc/ubuntu-minimal"):
        distribution_detection = Ubuntu()

    elif os.path.exists("/etc/debian_version"):
        distribution_detection = Debian()

    elif os.path.exists("/etc/gentoo-release"):
        distribution_detection = Gentoo()

    elif os.path.exists("/etc/slackware-version"):
        raise DistributionNotSupportedError("Slackware")

    elif os.path.exists("/var/lib/conarydb/conarydb"):
        distribution_detection = Conary()

    elif os.path.exists("/etc/arch-release"):
        distribution_detection = Arch()

    elif os.path.exists("/etc/release") and \
            re.match(".*Solaris", open("/etc/release", encoding="utf-8").readline()):
        distribution_detection = Solaris()

    elif os.path.exists("/etc/os-release") and \
            re.match(".*GNOME-Continuous", open("/etc/os-release",  encoding="utf-8").readline()):
        distribution_detection = GnomeContinuous()

    else:
        raise DistributionNotSupportedError("Unknown")

    LOGGING.debug(f"Detecting distribution: {distribution_detection.__class__.__name__}")

    return distribution_detection

distribution = detect_distribution()
package_database = distribution.package_database


### Backwards compatibility.

def detectDistro():  # pylint: disable=invalid-name
    """
    Detect Distribution. Wrapper over detect_distribution.
    """
    return detect_distribution()

distro = distribution
packageDb = package_database
