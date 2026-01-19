#!/usr/bin/python3

"""
Event listener demo.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=broad-exception-caught

# ruff: noqa: E402
# ruff: noqa: E501

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from time import sleep

# Explicit list of selected events:
# https://gitlab.gnome.org/GNOME/at-spi2-core/-/blob/HEAD/atspi/atspi-event-listener.c#L479

# Under Wayland the mouse events are not captured, possibly by design.

EVENT_NAMES = [
    "focus:",
    "mouse:rel",
    "mouse:button",
    "mouse:abs",
    "keyboard:modifiers",
    # The property-change event will trigger together with the sub-event, leaving it out for now.
    #"object:property-change",
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
    # Avoid swamping the log. Does not seem to do so on Wayland.
    #"object:bounds-changed",
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


def callback(event):
    """
    Event listener callback to be called when event is fired.

    :param event: Atspi Event.
    :type event: Atspi.Event
    """

    # Event given to callback is of type Atspi.Event.
    # http://lazka.github.io/pgi-docs/#Atspi-2.0/classes/Event.html

    # The Atspi.Accessible.
    source = event.source

    if isinstance(source, Atspi.Accessible):
        try:
            name = Atspi.Accessible.get_name(source)
            role_name = Atspi.Accessible.get_role_name(source)
            source_description = f"source: [ {role_name} | {name} ]"
        except Exception as e:
            source_description = f"[DEAD] - '{e}'"
    else:
        source_description = ""

    # Not printing any unnamed objects, which will flood the log.
    if "| ]" not in source_description:
        print(f"Event: '{event.type}' '{source_description}'")


EVENT_LISTENERS = {}
for event_name in EVENT_NAMES:

    try:
        listener = EVENT_LISTENERS[event_name]
    except Exception:
        print(f"Creating new event listener: '{event_name}' and registering it.")
        EVENT_LISTENERS[event_name] = Atspi.EventListener.new(callback)
        listener = EVENT_LISTENERS[event_name]

    Atspi.EventListener.register(listener, event_name)

try:

    # Global Interpreter Lock Release.
    def release_global_interpreter_lock():
        """
        Releasing the GIL or Global Interpreter Lock so we can catch an interrupt.
        """
        try:
            sleep(1e-2)
        except KeyboardInterrupt as e:
            # Store the exception for later.
            release_global_interpreter_lock.keyboard_exception = e
            Atspi.event_quit()
        return True

    # Make room for an exception if one occurs during the execution.
    release_global_interpreter_lock.keyboard_exception = None

    event_id = GLib.idle_add(release_global_interpreter_lock)
    # Enter the main loop to start receiving and dispatching events.
    Atspi.event_main()
    GLib.source_remove(event_id)
    if release_global_interpreter_lock.keyboard_exception is not None:
        # Raise an keyboard exception we may have gotten earlier.
        raise KeyboardInterrupt(release_global_interpreter_lock.keyboard_exception)

except KeyboardInterrupt as error:

    # Deregister the event.
    for event_name in EVENT_NAMES:

        try:
            listener = EVENT_LISTENERS[event_name]
        except Exception:
            pass

        print(f"Deregister event listener for event: '{event_name}'")
        Atspi.EventListener.deregister(listener, event_name)

    import sys
    print(f"Keyboard interrupt caught. Exiting script.\n{error}")

    sys.exit(0)
