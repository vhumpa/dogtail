#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release. Constants.
"""

import os

# Maybe do a configs as global variables?

SESSION_TYPE = "x11"
if "XDG_SESSION_TYPE" in os.environ and "wayland" in os.environ["XDG_SESSION_TYPE"]:
    os.system("gsettings set org.gnome.shell introspect true")
    SESSION_TYPE = "wayland"

LEFT = 1
RIGHT = 3

# Constants used to synthesize mouse events
MOUSE_BUTTON_EVENTS = {
    LEFT: {
        "press": "b1p",
        "release": "b1r",
        "click": "b1c",
        "double-click": "b1d",
    },
    RIGHT: {
        "press": "b3p",
        "release": "b3r",
        "click": "b3c",
        "double-click": "b3d",
    },

}
