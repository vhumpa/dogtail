#!/usr/bin/env python
# Dogtail demo script using tree.py
# FIXME: Use TC.
__author__ = 'Zack Cerza <zcerza@redhat.com'

from dogtail import tree
from dogtail.utils import run
from dogtail.predicate import GenericPredicate
from time import sleep
from os import environ, path, remove
environ['LANG']='en_US.UTF-8'

# Remove the output file, if it's still there from a previous run
if path.isfile(path.join(path.expandvars("$HOME"), "Desktop", "UTF8demo.txt")):
    remove(path.join(path.expandvars("$HOME"), "Desktop", "UTF8demo.txt"))

# Start gedit.
run("gedit")

# Get a handle to gedit's application object.
gedit = tree.root.application('gedit')

# Get a handle to gedit's text object.
# Last text object is the gedit's text field
textbuffer = gedit.findChildren(GenericPredicate(roleName='text'))[-1]

# This will work only if 'File Browser panel' plugin is disabled
#textbuffer = gedit.child(roleName = 'text')

# Load the UTF-8 demo file.
from sys import path
utfdemo = open(path[0] + '/data/UTF-8-demo.txt', 'r')

# Load the UTF-8 demo file into gedit's text buffer.
textbuffer.text = utfdemo.read()

# Get a handle to gedit's File menu.
filemenu = gedit.menu('File')

# Get a handle to gedit's Save button.
savebutton = gedit.button('Save')

# Click the button
savebutton.click()

# Get a handle to gedit's Save As... dialog.
try:
    saveas = gedit.child(roleName='file chooser')
except tree.SearchError:
    try:
        saveas = gedit.dialog('Save As\\u2026')
    except tree.SearchError:
        saveas = gedit.dialog('Save as...')

# We want to save to the file name 'UTF8demo.txt'.
saveas.child(roleName = 'text').text = 'UTF8demo.txt'

# Save the file on the Desktop

# Don't make the mistake of only searching by name, there are multiple
# "Desktop" entires in the Save As dialog - you have to query for the
# roleName too - see the on-line help for the Dogtail "tree" class for
# details
saveas.child('Desktop', roleName='table cell').click()

#  Click the Save button.
saveas.button('Save').click()

# Let's quit now.
filemenu.click()
filemenu.menuItem('Quit').click()
