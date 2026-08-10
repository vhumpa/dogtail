#!/usr/bin/python3
"""
Application under test for test_hermetic_gtk3.py.

A button, a label that says whether it got clicked, and an entry to type into.
That is it.
"""

import sys

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GLib, Gtk  # pylint: disable=wrong-import-position


def main():
    """
    Build and run the test window.
    """

    windowed = "--windowed" in sys.argv

    # At-spi names the application after prgname, so the windowed variant needs
    # its own to be told apart.
    if windowed:
        GLib.set_prgname("hermetic_app_windowed")

    window = Gtk.Window(title="dogtail hermetic test app")
    window.set_default_size(400, 200)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    window.add(box)

    label = Gtk.Label(label="not clicked")
    box.pack_start(label, True, True, 0)

    button = Gtk.Button(label="click me")
    button.connect("clicked", lambda _button: label.set_text("clicked"))
    box.pack_start(button, True, True, 0)

    entry = Gtk.Entry()
    entry.set_placeholder_text("type here")
    box.pack_start(entry, True, True, 0)

    window.connect("destroy", Gtk.main_quit)

    # Fullscreen, so that window coordinates equal screen coordinates. The
    # --windowed flag is for the test that checks the guard refuses the rest.
    if not windowed:
        window.fullscreen()

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
