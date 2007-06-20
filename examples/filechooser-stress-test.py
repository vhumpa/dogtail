#!/usr/bin/env python
# Stress test: repeatedly open and close the filechooser dialog

from dogtail.procedural import *

import dogtail.i18n
dogtail.i18n.loadTranslationsFromPackageMoFiles('gedit')

run('gedit')

while True:
    click('Open...')
    try:
        focus.dialog(u'Open Files\u2026')
    except FocusError:
        focus.dialog(u'Open Files...')
    click('Cancel')
