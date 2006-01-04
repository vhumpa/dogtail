#!/usr/bin/env python
# Dogtail demo script

from dogtail.config import config
#config.debugSearching = True
#config.debugTranslation = True

import dogtail.tc
from dogtail.procedural import *
from dogtail.utils import screenshot

# These next two lines get us translations for free. To see the script run
# translated, run it like this: 
#  LANG=ja_JP.UTF-8 ./gedit-test-utf8-procedural-api.py
# You might also want to set config.debugTranslation and 
# config.debugSearching to True, just for fun.
import dogtail.i18n
dogtail.i18n.loadTranslationsFromPackageMoFiles('gedit')

from os import environ, path, remove

# Load our persistent Dogtail objects
TestString = dogtail.tc.TCString()
TestImage = dogtail.tc.TCImage()

# Remove the output file, if it's still there from a previous run
if path.isfile(path.join(path.expandvars("$HOME"), "Desktop", "UTF8demo.txt")):
	remove(path.join(path.expandvars("$HOME"), "Desktop", "UTF8demo.txt"))

# Start gedit.
run('gedit')

# Set focus on gedit
focus.application('gedit')

# Focus gedit's text buffer.
focus.text()

# Load the UTF-8 demo file.
from sys import path
utfdemo = file(path[0] + '/data/UTF-8-demo.txt')

# Load the UTF-8 demo file into the text buffer.
focus.widget.text = utfdemo.read()

# Take a screenshot of the window
screenshot()

# Click gedit's Save button.
click('Save')

# Focus gedit's Save As... dialog
focus.dialog('Save as...')

# click the Browse for other folders widget
activate('Browse for other folders')

# Click the Desktop widget
activate('Desktop', roleName = 'table cell')

# We want to save to the file name 'UTF8demo.txt'.
focus.text()
focus.widget.text = 'UTF8demo.txt'

# Click the Save button.
click('Save')

# Let's quit now.
click('Quit')

# We have driven gedit now lets check to see if the saved file is the same as 
# the baseline file

# Read in the "gold" file
try:
	gold = open(path[0] + '/data/UTF-8-demo.txt', 'r').readlines()
except IOError:
	print "File open failed"

# Read the test file for comparison
filepath = environ['HOME'] + '/Desktop/UTF8demo.txt'
testfile = open(filepath, 'r').readlines()

# We now have the original and saved files as lists. Let's compare them line
# by line to see if they are the same
i = 0
for baseline in gold:
	label = "line test " + str(i + 1)
	TestString.compare(label, baseline, testfile[i], encoding='utf-8')
	i = i + 1

