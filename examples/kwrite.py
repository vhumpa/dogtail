#!/usr/bin/env python3
# Dogtail demo script using KWrite (QT / KDE)
__author__ = "Max Gaukler <development@maxgaukler.de>"

# SPDX-License-Identifier: CC0-1.0
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

from dogtail import tree
from dogtail.predicate import *
import subprocess
import time

# Start the KWrite application with English localization and enabled accessibility.
# (see also: dogtail.utils.run())
# For other languages, you would have to change the texts in this script.
subprocess.Popen("LANG=C QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1 kwrite", shell=True)

# Connect
app = tree.root.application("kwrite")

# Show all elements
app.dump()

# Open the "About KDE" dialog and close it again.

# Note that to open a sub-menu entry, you must first open the corresponding main menu entry.
app.child("Help").click()
app.child("About KDE").click()
# Most of the time, .child() is good enough. If the label is not unique, you can create a more specific search
# - by type (.dialog, .button, ...) and by nesting items
# - or by other attributes (roleName, ...)
app.dialog("About KDE").button("Close").click()

# Check that the dialog is gone
time.sleep(1)
assert not app.isChild(IsADialogNamed("About KDE"))

# Write something into the text of the new file
t = app.child(roleName="text")
assert t.text == ""
t.set_text_contents("Hello World")
assert t.text == "Hello World"


# File -> Quit -> Discard
app.child("File").click()
app.child("File").child("Quit").click()
app.dialog("Close Document").child("Discard").click()
