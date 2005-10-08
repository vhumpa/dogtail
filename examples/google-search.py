#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

# Test of filling in a form in a web browser
# Under construction.  Doesn't yet work

from dogtail.apps.wrappers.epiphany import *

class GoogleFrontPage(Node):
    def __init__(self, node):
        Node.__init__(self, node)
        self.searchButton = self.button('Google Search')
        self.imFeelingLuckyButton = self.button("I'm Feeling Lucky")

        # Locate the text entry dialog as a sibling of the search button
        self.textEntry = self.searchButton.parent.child(roleName='text', debugName='Search String Text Entry')

import dogtail.config
dogtail.config.Config.debugSearching=True

# Epiphany doesn't seem to set the sensitivity state on buttons in web pages:
dogtail.config.Config.ensureSensitivity=False

wb = EpiphanyApp()

# Browse to Google front page
tab = wb.browseToUrl("http://www.google.com")
tab.dump()

gfp = GoogleFrontPage(tab)

# Debug dump:
gfp.child(roleName='text').dump()

# Do a search:
gfp.textEntry.text = "zombie pirates"
print gfp.searchButton.actions[0]
gfp.searchButton.press()


# Scrape out the results:
frame = gfp.child(roleName='frame')
results = frame.findAllChildrenSatisfying(GenericPredicate(roleName='text'), recursive=False)
for result in results:
    print "Result:"
    print result.text
    print "--------------------------------------"



