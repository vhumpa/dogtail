#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

# Test opening a new window and browsing to a local HTML file

# Under construction.  Doesn't yet work

from dogtail.apps.wrappers.mozilla import *

import dogtail.config
dogtail.Config.debugSearching=True

ff = FirefoxApp()
wnd = ff.newWindow()
wnd.browseTo("file://"+path.abspath("data/test.html"))
