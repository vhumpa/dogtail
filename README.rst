dogtail
=======

dogtail is a GUI test tool and UI automation framework written in Python. It uses Accessibility (a11y) technologies to communicate with desktop applications. dogtail scripts are written in Python and executed like any other Python program.

Dogtail works great in combination with behave and qecore (based on behave and dogtail), especially if you're interested in using it with modern Wayland-based GNOME. Please see this article for more details on how we mainly use it:
`Automation through accessibility <https://fedoramagazine.org/automation-through-accessibility/>`_.

Other than that, dogtail should work with any desktop environment that still runs atspi with Xorg.

News
====

dogtail 1.0
-----------

After more than five years of continuous experimentation and development, we are excited to finally release Dogtail 1.0—a Wayland-enabled version of Dogtail! How did we achieve this? It was made possible by the `gnome-ponytail-daemon <https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon>`_, originally crafted by Olivier Fourdan. This tool allows us to perform actions in a Wayland GNOME session in a similar way to how we have been doing so with X functions.

dogtail 1.0.2 - Cummulated two updates - bugfixes - and releasing as minor release. 
Update for sniff: Switched using XPM icons to PNG as the most recent gdk pixbug no longer supports them
(fixes no icons in most recent system) - thanks to Jiri Prajzner
Using specific configuration for the debug logger to prevent duplicit logging - MR#39 - thanks to Jiri Kortus


dogtail 1.0.1 - Rebased with a number of contributions that were done to the master branch while we were working on Wayland and we have accidentaly not included them in 1.0.
See https://gitlab.com/dogtail/dogtail/-/issues/31

Also returned couple of modules we thought were of no use (tc, wrapped) but were proved otherwise to keep 1.0 fully compatible with 0.x.

How does it work in brief?
--------------------------

The core functionality relies on the Screen Cast and Remote Desktop API, enabling us to "connect" to either a specific window or the entire screen to simulate user input actions like key presses, typing, and—most importantly—mouse actions on specific coordinates. Ponytail uses the window list from ``org.gnome.Shell.Introspect`` to identify windows. Dogtail then ensures the correct window is connected via the Remote Desktop API, allowing input actions to be accurately executed within it.

On the AT-SPI tree and accessibility's "introspection" side, not much has changed—input has primarily been the challenge on Wayland. The main difference is that only "local" window coordinates are known for UI items. To address this, we always connect to the specific window we're working with, and Ponytail's ``connectWindow`` ensures these local coordinates are translated to global ones internally.

What does this mean for users?
------------------------------

Dogtail handles all of this logic seamlessly, so in practical use, the user doesn't need to worry about coordinate types or window connections. In fact, the vast majority of our tests work identically in both X and Wayland sessions using the Dogtail API. When running on an X session, Dogtail will use the traditional X functions to handle input and operate as it always has.

A long journey to 1.0
---------------------

We began working on the Wayland-enabled version over five years ago (originally available in the ``devel/wayland`` branch). It has taken all this time to ensure the solution is robust and reliable enough to warrant a 1.0 release. This version includes all the Wayland-related developments and other changes (like the GTK4 support tweaks mentioned below) and has been extensively tested. Importantly, it is backward compatible with the entire Dogtail API that has been available so far. This release includes all modules from the 0.9.x series, most notably the "procedural" module, which we plan to deprecate in favor of a completely "tree-based" approach in Dogtail 2.0.

That release will also involve significant cleanup, major code refactoring, and a transition from ``pyatspi`` to directly introspected ``atspi``. It will also contain updated code examples and Dogtail's unittests should pass with GitLab pipelines re-enabled.

For more details on these upcoming changes, see issue #29.

1.0+ Important: Handling GTK4 Application Windows in Dogtail
------------------------------------------------------------

For GTK4 applications, disabling window shadows is essential to ensure accurate positioning by Dogtail. With shadows disabled, we encounter a consistent coordinate offset, which we've preconfigured as ``dogtail.config.gtk4Offset``. In the case of working with fullscreen windows, the offset is 0, and we manage to detect that on-the-fly both in X11 and Wayland sessions. However, this process requires ``python-xlib``, even for Wayland sessions, leveraging Xwayland to ascertain resolution information, as no more direct method we've found is currently available for Wayland.

When window shadows are active, the perceived offset can vary significantly, influenced by factors such as the specific application, window size, and scaling settings. To ensure consistent behavior across applications, disabling shadows is recommended.

Disabling Shadows in GTK4:

To disable window shadows, add the following CSS to your GTK4 configuration (``~/.config/gtk-4.0/gtk.css``):

.. code-block:: css

    window, .popover, .tooltip {
        box-shadow: none;
    }

Installation
============

Dogtail is available with PIP! (1.0 inclusion pending). If you'd like to use it with Wayland GNOME, you also need to get the ``dogtail-ponytail-daemon``: https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon. We do not have that as a dependency in PIP as it compiles C code.

Check your distro for packages! If not at the latest version, we also have released tarballs for download: https://gitlab.com/dogtail/dogtail/tree/released

For details see the INSTALL file.

Dependencies
============

Python bindings for your distribution, e.g. python-apt or rpm-python

PyGObject and GNOME-Python

Applications to test, e.g. from the GNOME desktop: http://gnome.org/

Using
=====

Currently, GNOME and GTK+ applications are supported, in both Xorg and Wayland sessions.
See examples for direct dogtail use or check the following article for more information: 
`Automation through accessibility <https://fedoramagazine.org/automation-through-accessibility/>`_.

If you are using KDE instead, set the environment variable ``QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1`` when launching the respective program. 
You can add this line to your profile file:

.. code-block:: bash

    export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1

Depending on the version, ``QT_ACCESSIBILITY=1`` may be needed instead.

For very old KDE/QT versions (approximately 4.8.3 to 5.0), you have to install the ``qt-at-spi`` QT plugin and set the environment variable ``QT_ACCESSIBILITY`` to 1.

First, enable accessibility support in your GNOME session with the following command:

.. code-block:: bash

    gsettings set org.gnome.desktop.interface toolkit-accessibility true

This only affects newly-started applications, so you may want to log out and log back in again.

Should you run ``sniff`` first, or be using ``dogtail-run-headless-next`` or ``qecore-headless`` scripts to handle your sessions, the accessibility will be auto-enabled for you.

Bugs
====

Please report any bugs at:
    https://gitlab.com/dogtail/dogtail/issues

Contact
=======

Website:
    https://gitlab.com/dogtail/dogtail/

Issue tracker:
    https://gitlab.com/dogtail/dogtail/issues

API Documentation:
    http://fedorapeople.org/~vhumpa/dogtail/epydoc/

We have deprecated our mailing lists as well as the IRC channel. Please use our GITLAB for issues and merge requests! (Or possibly https://github.com/vhumpa/dogtail for your pull requests should you prefer to use GitHub, but gitlab.com is preferred)
