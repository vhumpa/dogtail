#!/usr/bin/env python
# Dogtail demo script
# Note that this script is outdated and may cause your session to lock up until
# it is killed. It will most likely be deleted in the next release.
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

import dogtail.tree
import pyatspi
import Accessibility

# Test of event callbacks
# Under construction

def callback(event):
    source = event.source
    if isinstance(source, Accessibility.Accessible):
        sourceStr = " source:%s"% str(source)
    else:
        sourceStr = ""
    print "Got event: %s%s"%(event.type, sourceStr)

#listener = atspi.EventListener(callback, ["window:create"])
#listener = atspi.EventListener(callback, ["focus:", "object:", "window:"])
#listener = atspi.EventListener(callback, ["window:"])
#listener = atspi.EventListener(callback, ["object:"])
#listener = atspi.EventListener(callback, ["focus:"])

# explicit list of all events, taken from at-spi/test/event-listener-test.c:
eventNames = [
    "focus:",
    "mouse:rel",
    "mouse:button",
    "mouse:abs",
    "keyboard:modifiers",
    "object:property-change",
    "object:property-change:accessible-name",
    "object:property-change:accessible-description",
    "object:property-change:accessible-parent",
    "object:state-changed",
    "object:state-changed:focused",
    "object:selection-changed",
    "object:children-changed",
    "object:active-descendant-changed",
    "object:visible-data-changed",
    "object:text-selection-changed",
#    "object:text-caret-moved",
#    "object:text-changed",
    "object:column-inserted",
    "object:row-inserted",
    "object:column-reordered",
    "object:row-reordered",
    "object:column-deleted",
    "object:row-deleted",
    "object:model-changed",
    "object:link-selected",
    #"object:bounds-changed", # avoid swamping log
    "window:minimize",
    "window:maximize",
    "window:restore",
    "window:activate",
    "window:create",
    "window:deactivate",
    "window:close",
    "window:lower",
    "window:raise",
    "window:resize",
    "window:shade",
    "window:unshade",
    "object:property-change:accessible-table-summary",
    "object:property-change:accessible-table-row-header",
    "object:property-change:accessible-table-column-header",
    "object:property-change:accessible-table-summary",
    "object:property-change:accessible-table-row-description",
    "object:property-change:accessible-table-column-description",
    "object:test"
    ]

listeners = []
for eventName in eventNames:
    #listener = atspi.EventListener(callback, [eventName])
    listeners.append(pyatspi.Registry.registerEventListener(callback, eventName))

#listener = atspi.EventListener(callback, [""])
pyatspi.Registry.start(False, False)
