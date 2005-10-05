#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

# Test importing an email that crashed older versions of Evolution
#
# Assumes evolution is configured and is running
#
# CAN-2005-0806.mbox is attachment 44836 in bugzilla.gnome.org
# It is an email attached to bug 272609 (which was bug 72609 in the bugzilla.ximian.com)
# which crashed an unpatched Evolution 2.0.3 when opened.
# See http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CAN-2005-0806

from dogtail.apps.wrappers.evolution import *

evo = EvolutionApp()
evo.importSingleEmail(path.abspath("data/CAN-2005-0806.mbox"))
