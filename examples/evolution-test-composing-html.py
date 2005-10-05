#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

# Test composing (and sending) an HTML email

# Under construction.  Doesn't yet work

# FIXME:  partially rewrite; this would be a great example of a script using both APIs;  the typing stuff would work better with the procedural interface

from dogtail.apps.wrappers.evolution import *

evo = EvolutionApp()
composer = evo.composeEmail()
composer.to = "dmalcolm@redhat.com"
composer.subject = "Yarrrrrr!!!"
composer.setHtml(True)
composer.setHeader(1)
composer.typeText("Leveraging Synergies\n\n")
composer.setBulletedList()
composer.typeText("pirates!\n")
composer.typeText("zombies!\n")
composer.typeText("zombie pirates!")

#composer.testUndoRedo()
# unfortunately, undo doesn't seem to desensitize correctly in Evolution 2.4

composer.send()
