#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

# Tries to start every user-visible application in the GNOME panel
# FIXME: this doesn't yet work

from dogtail.apps.wrappers.gnomepanel import *

import dogtail.config
dogtail.config.Config.debugSearching=True

panel = GnomePanel()
for launcher in panel.applications():
	print launcher
	sleep(5) # really need this for sanity's sake!
	launcher.click()    
	

    
