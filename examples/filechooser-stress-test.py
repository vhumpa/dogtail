#!/usr/bin/env python
# Stress test: repeatedly open and close the filechooser dialog

import dogtail.tree
from dogtail.apps.wrappers.gcalctool import *
import dogtail.utils

dogtail.utils.run('gedit')
app = dogtail.tree.root.application('gedit')

while True:
	app.menu('File').menuItem('Open...').click()
	app.dialog('Open File...').button('Cancel').click()

