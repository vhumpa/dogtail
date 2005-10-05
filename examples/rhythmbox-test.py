#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

# Test playing a specific song in Rhythmbox, using the procedural API:
# FIXME: not yet finished (barely started, in fact)
# FIXME: doesn't work yet.  Tested with Rhythmbox 0.8.8  on FC3

from dogtail.procedural import *
from dogtail.utils import *

run("rhythmbox")

focus.application('rhythmbox') #FIXME: shouldn't 'run' automatically scope the app?  this call seems to be needed

# name='Artist', roleName='table column header'

# name='Album', roleName='table column header'



