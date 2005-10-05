#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

# Test AbiWord, converting a Word document to HTML, using the procedural API.
# Also shows how to write code that handles different versions of a package,
# querying the installed package version in a distribution-neutral fashion.
# FIXME: not yet finished
# FIXME: doesn't work yet.  Tested with AbiWord 2.0.12 on FC3

from dogtail.procedural import *
from dogtail.utils import *
from dogtail.distro import *
from dogtail.version import Version

abiVersion = packageDb.getVersion('abiword')

# Set up appname based on version of abiword:
if abiVersion>=Version([2,3,0]):
	appName = 'AbiWord-2.4'
else:
	appName = 'AbiWord'

run("abiword", appName=appName)


print "foo"

focus.application(appName) #FIXME: shouldn't 'run' automatically scope the app?  this call seems to be needed

print "bar"

focus.menu('File')
click('Open...')

# On AbiWord 2.0.12 on FC3 this gives a GtkFileSelector dialog:
focus.dialog('Open File')  # fails on FC3: the dialog has roleName="file chooser", rather than 'dialog'
focus.text()
focus.widget.object.text = "test-word-document.doc"
# FIXME: path issues

click('OK')

focus.menu('File')
click('Save As...')
