# dogtail

**dogtail** is a GUI test tool and UI automation framework written in Python. It uses Accessibility (AT-SPI) technologies to communicate with desktop applications. **dogtail** scripts are written in Python and executed like any other Python program.

Dogtail works great in combination with behave and qecore (expands on behave and dogtail), but you can use it alone as well. If you're interested in using it with modern wayland-based GNOME. Please see this article for more details on how we mainly use it: https://fedoramagazine.org/automation-through-accessibility/

Other than that, dogtail should work with any desktop environment that still runs Atspi with Xorg.


# News

## Release of dogtail-2.x

Detailed information can be found in issue https://gitlab.com/dogtail/dogtail/-/issues/29.

To shortly summarize, there were a few reasons for this project to be rewritten.

 - Dogtail's code base was not in a best state as years of workarounds and patches have left their mark.
 - Possibility of a new Accessibility architecture - AccessKit/Newton. The idea of this project was quite appealing as it could possibly solve many issues we have with AT-SPI.

I started to look into it and what it would take to make all necessary changes so we could work with Newton as well as Atspi. Changing dogtail-1.x to include Newton would be a challenge and changes would be required all over the place. Even if done well, once there would be another change it the future, the work required would once again be massive.

The easiest solution seemed to redo the project from the scratch. Thoughts were to create a new project altogether but we settled on doing the changes in the dogtail project and provide improvements for others as well, in the spirit of open source.

I believe we now have a dogtail with a refactored code base that is more approachable, readable and maintainable. If another Accessibility architecture would be created in the future, including it in dogtail would be simple.


# Installation

## Installation from GitLab, clone and install:
```
git clone https://gitlab.com/dogtail/dogtail.git
cd dogtail
git checkout devel/release-2.0 # Will become 'main' in the future. #TODO change before merge to main.
python3 -m build
sudo pip3 install dist/dogtail-2.*-py3-none-any.whl --force-reinstall
```

## Installation from GitLab, pip install:
```
sudo dnf install python3-pip
sudo python3 -m pip install git+https://gitlab.com/dogtail/dogtail@devel/release-2.0 #TODO change before merge to main.
```

## Installation from pypi:

```
sudo python3 -m pip install dogtail.
```

## Installation from Package Registry:

You can install this package from GitLab Package Registry. Visit https://gitlab.com/dogtail/dogtail/-/packages/, download the file and install it. These are built automatically with CI.


# Dependencies

Python bindings for your distribution, e.g. python-apt or rpm-python. PyGObject and GNOME-Python.

Applications to test, e.g. from the GNOME desktop:
- http://gnome.org/

If you'd like to use it with Wayland GNOME, you also need to get the gnome-ponytail-daemon:
- https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon.

We do not have that as a dependency in pip as it compiles C code. Install from source, if your distribution does not have the gnome-ponytail-daemon in the repositories.
```
sudo dnf install meson gcc glib2-devel
git clone https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon.git
cd gnome-ponytail-daemon
sudo meson setup build
sudo ninja -C build
sudo ninja -C build install
```

# Something is missing in dogtail-2.x that was present in 1.x?

In a quest for a better and maintainable code I went over everything and removed what I deemed not useful or redundant. A lot of what I removed can be replaced with other parts, no longer works or was never observed in use by our team.

I am not perfect. If something I have removed is useful to you, let me know in the [Issues](https://gitlab.com/dogtail/dogtail/issues). While a lot of stuff was removed deliberately, and I can show you how to do things with what is present, something could have slipped through, and I could have removed a very useful part.

I have chosen the approach to remove what I can, and return it on request if it is valid enough as apposed to dragging a code with us that I have never seen in use.


# Wayland

Usage on Wayland was made possible by the `gnome-ponytail-daemon`, originally crafted by Olivier Fourdan: https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon. This tool allows us to perform actions in a Wayland GNOME session in a similar way to how we have been doing with X functions.

## How does it work?

The core functionality relies on the Screen Cast and Remote Desktop API, enabling us to "connect" to either a specific window or the entire screen to simulate user input actions like key presses, typing, and **most importantly** mouse actions on specific coordinates. Ponytail uses the window list from `org.gnome.Shell.Introspect` to identify windows. Dogtail then ensures the correct window is connected via the Remote Desktop API, allowing input actions to be accurately executed within it.

On the AT-SPI tree and accessibility's "introspection" side, not much has changed - input has primarily been the challenge on Wayland. The main difference is that only "local" window coordinates are known for UI items. To address this, we always connect to the specific window we're working with, and Ponytail's `connectWindow` ensures these local coordinates are translated to global ones internally.

## What does this mean for users?

Dogtail handles all of this logic seamlessly, so in practical use, the user doesn't need to worry about coordinate types or window connections. In fact, the vast majority of our tests work identically in both X and Wayland sessions using the Dogtail API. When running on an X session, Dogtail will use the traditional X functions to handle input and operate as it always has.


# Important: Handling GTK4 Application Windows in Dogtail

For GTK4 applications, disabling window shadows is essential to ensure accurate positioning by Dogtail. With shadows disabled, we encounter a consistent coordinate offset, which we've pre-configured as `dogtail.config.offset`. In case of working with full screen windows, the offset is 0, and we manage to detect that on-the-fly both in x11 and wayland sessions. However, this process requires `python-xlib`, even for Wayland sessions, leveraging Xwayland to ascertain resolution information, as no more direct method we've found currently available for Wayland.

When window shadows are active, the perceived offset can vary significantly, influenced by factors such as the specific application, window size, and scaling settings. To ensure consistent behavior across applications, disabling shadows is recommended.

Disabling Shadows in GTK4:

To disable window shadows, add the following CSS to your GTK4 configuration (`~/.config/gtk-4.0/gtk.css`):

```
window, .popover, .tooltip {
    box-shadow: none;
}
```

# Using

Currently GNOME and GTK+ applications are supported. Both Xorg and Wayland sessions.

See examples for direct dogtail use or check: https://fedoramagazine.org/automation-through-accessibility/

Thanks to qt-at-spi KDE4 and QT applications are now available too, feel free to try, but it's no longer supported from us, might be better to check KDE's native solutions.

First, enable accessibility support in your GNOME session with:
```
gsettings set org.gnome.desktop.interface toolkit-accessibility true
```

This only affects newly-started applications, so you may want to log out and log back in again.

Should you use 'dogtail-headless' or 'qecore-headless' scripts to handle your sessions, the accessibility will be auto enabled for you.


## Atspi API references
 - http://lazka.github.io/pgi-docs/#Atspi-2.0
 - https://docs.gtk.org/atspi2/index.html


# Bugs
Please report any bugs at:
    https://gitlab.com/dogtail/dogtail/issues


# Contact
Website:
- https://gitlab.com/dogtail/dogtail/

Issue tracker:
- https://gitlab.com/dogtail/dogtail/issues

API Documentation:
- http://fedorapeople.org/~vhumpa/dogtail/epydoc/ # TODO, documentation is not finished for dogtail-2.x

We have deprecated our mailing lists as well as IRC channel. Please use our GitLab for issues and merge requests! (Or possibly https://github.com/vhumpa/dogtail perhaps for your pull requests should you prefer to use github, but gitlab.com is preferred)


# Contributing

- **Bug Reports**: If you find a bug, check if an [issue](https://gitlab.com/dogtail/dogtail/issues) already exists. If not, please open one with a clear description and steps to reproduce it.

- **Feature Ideas**: Have a great idea? Open an [issue](https://gitlab.com/dogtail/dogtail/issues) to discuss it. This helps us align on the goal before you write any code.

- **Ready to Help**? Look for existing [issues](https://gitlab.com/dogtail/dogtail/issues). If you see one you'd like to work on, just leave a comment to let us know!

There are a few ways I would like to preserve the readability of the code.

- For functions and methods, use docstring to explain what it does, this way we can be sure it gets in the documentation.
- Use correct casing for classes, methods and variables. Most of the code base uses *snake_case*.
- Use full names for variables where possible. Single letter variables are not acceptable.
- Comments are sentences, they start with a capital letter and end with a dot.

# Version dogtail-1.x

The [dogtail-1.x](https://gitlab.com/dogtail/dogtail/-/tree/dogtail-1.x) is still available and if required will be updated and new versions will be released.
