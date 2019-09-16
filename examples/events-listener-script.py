# -*- coding: utf-8 -*-

# Event listener demo.
__author__ = "David Malcolm <dmalcolm@redhat.com>"

import pyatspi
import Accessibility

# Test of event callbacks
# Under construction

def callback(event):
    source = event.source
    if isinstance(source, Accessibility.Accessible):
        source_description = "source:'%s'"% str(source)
    else:
        source_description = ""

    # Not printing any unnamed objects, which will flood the log.
    if not "| ]" in source_description:
        print(("Event: %s %s"%(event.type, source_description)))

# explicit list of all events, taken from at-spi/test/event-listener-test.c:
EVENT_NAMES = [
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
    "object:text-caret-moved",
    "object:text-changed",
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

EVENT_LISTENERS = []
for event_name in EVENT_NAMES:
    EVENT_LISTENERS.append(pyatspi.Registry.registerEventListener(callback, event_name))

try:
    pyatspi.Registry.start(False, True)
except KeyboardInterrupt as error:
    import sys
    print("Keyboard interupt caught. Exiting script.\n" + str(error))
    sys.exit(0)
