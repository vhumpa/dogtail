#!/usr/bin/python3
"""
Application under test for test_hermetic_gtk4.py.

The same three widgets as hermetic_app_gtk3.py, built with GTK4 so that the
hermetic session gets tested against both toolkits.
"""

import sys

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk  # pylint: disable=wrong-import-position


def main():
    """
    Build and run the test window.
    """

    windowed = "--windowed" in sys.argv

    # At-spi names the application after prgname, so the windowed variant needs
    # its own to be told apart.
    GLib.set_prgname("hermetic_app_windowed_gtk4" if windowed else "hermetic_app_gtk4")

    Gtk.init()
    loop = GLib.MainLoop()

    window = Gtk.Window(title="dogtail hermetic test app")
    window.set_default_size(400, 200)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    window.set_child(box)

    label = Gtk.Label(label="not clicked")
    box.append(label)

    button = Gtk.Button(label="click me")
    button.connect("clicked", lambda _button: label.set_text("clicked"))
    box.append(button)

    entry = Gtk.Entry()
    entry.set_placeholder_text("type here")
    box.append(entry)

    window.connect("close-request", lambda *_args: loop.quit())

    # Fullscreen, same reason as the GTK3 fixture.
    if not windowed:
        window.fullscreen()

    window.present()
    loop.run()


if __name__ == "__main__":
    main()
