#!/usr/bin/env python
# Stress test: repeatedly open and close the filechooser dialog

from dogtail.procedural import *

run('gedit')

while True:
	click('Open...')
	focus.dialog('Open File...')
	click('Cancel')

