#!/usr/bin/env python
# Dogtail demo script using tree.py
# FIXME: Use TC.
__author__ = 'Zack Cerza <zcerza@redhat.com'

from dogtail import tree
from dogtail.utils import run
from time import sleep
from os import environ, path
environ['LANG']='en_US.UTF-8'

# Remove the output file, if it's still there from a previous run
if path.isfile(path.join(path.expandvars("$HOME"), "Desktop", "UTF8demo.txt")):
	remove(path.join(path.expandvars("$HOME"), "Desktop", "UTF8demo.txt"))

# Start gedit.
run("gedit")

# Get a handle to gedit's application object.
gedit = tree.root.findChild(name = 'gedit', roleName = 'application')

# Get a handle to gedit's text object.
textbuffer = gedit.findChild(roleName = 'text')

# Load the UTF-8 demo file.
from sys import path
utfdemo = file(path[0] + '/data/UTF-8-demo.txt')

# Load the UTF-8 demo file into gedit's text buffer.
textbuffer.text = utfdemo.read()

# Get a handle to gedit's File menu.
filemenu = gedit.findChild(name = 'File', roleName = 'menu')

# Get a handle to gedit's Save button.
savebutton = gedit.findChild(name = 'Save', roleName = 'push button')

# Click the button and wait a second.
savebutton.click()
sleep(1)

# Get a handle to gedit's Save As... dialog.
saveas = gedit.findChild(name = 'Save as...', roleName = 'dialog')

# We want to save to the file name 'UTF8demo.txt'.
saveas.findChild(roleName = 'text').text = 'UTF8demo.txt'

# Let's save it to the desktop.
saveas.findChild(name = 'Desktop', roleName = 'menu item').click()
sleep(0.25)

# Click the Save button.
saveas.findChild(name = 'Save', roleName = 'push button').click()
sleep(0.5)

# Let's quit now.
filemenu.findChild(name = 'Quit').click() 

