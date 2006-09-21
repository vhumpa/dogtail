#!/usr/bin/env python
# Stress test: repeatedly open and close the filechooser dialog

from dogtail.procedural import *

run('gedit')

while True:
    click('Open...')
    focus.dialog(u'Open Files\u2026')
    click('Cancel')
