#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

# i18n tests

from dogtail.tree import root

import dogtail.i18n
import dogtail.distro

def translateAllStrings(appName):
    """
    Test of the translation functions.

    Take all user-visible strings in an app that's running in the default locale
    and try translating them all into the locale that this script is running in.
    """
    for string in root.application(appName).getUserVisibleStrings():
        print "User-visible string: %s"%string
        print "Translation is:%s"%dogtail.i18n.translate(string)

print "Package dependencies: %s"%dogtail.distro.packageDb.getDependencies('evolution')
#print dogtail.i18n.getMoFilesForPackage('evolution', True)
print "Translation domains: %s"%dogtail.i18n.getTranslationDomainsForPackage('evolution', True)

#dogtail.i18n.loadTranslationsFromPackageMoFiles('evolution')
#translateAllStrings('evolution')
