dogtail is a GUI test tool and UI automation framework written in Python. It uses Accessibility (a11y) technologies to communicate with desktop applications. dogtail scripts are written in Python and executed like any other Python program.

Dogtails works great in combination with behave and qecore (based on behave and dogtail) (not only) if you're interested in using it with modern wayland-based GNOME. Please see this article for more details on how we mainly use it: https://fedoramagazine.org/automation-through-accessibility/

Other than that, dogtail should work with any desktop environment that still runs atspi with Xorg.


News
====
# dogtail 1.0

After more than five years of continuous experimentation and development, we are excited to finally release Dogtail 1.0—a Wayland-enabled version of Dogtail! How did we achieve this? It was made possible by the `gnome-ponytail-daemon`, originally crafted by Olivier Fourdan: https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon. This tool allows us to perform actions in a Wayland GNOME session in a similar way to how we have been doing so with X functions.

### dogtail 1.0.1

Rebased with a number of contributions that were done to the master branch while we were working on Wayland and we have accidentaly not included them in 1.0.
See https://gitlab.com/dogtail/dogtail/-/issues/31 

Also returned couple of modules we thought were of no use (tc, wrapped) but were proved otherwise to keep 1.0 fully compatible with 0.x.

### dogtail 1.0.2

Cummulated two updates - bugfixes - and releasing as minor release. 
Update for sniff: Switched using XPM icons to PNG as the most recent gdk pixbug no longer supports them
(fixes no icons in most recent system) - thanks to Jiri Prajzner
Using specific configuration for the debug logger to prevent duplicit logging - MR#39 - thanks to Jiri Kortus

## How does it work in brief?

The core functionality relies on the Screen Cast and Remote Desktop API, enabling us to "connect" to either a specific window or the entire screen to simulate user input actions like key presses, typing, and—most importantly—mouse actions on specific coordinates. Ponytail uses the window list from `org.gnome.Shell.Introspect` to identify windows. Dogtail then ensures the correct window is connected via the Remote Desktop API, allowing input actions to be accurately executed within it.

On the AT-SPI tree and accessibility's "introspection" side, not much has changed—input has primarily been the challenge on Wayland. The main difference is that only "local" window coordinates are known for UI items. To address this, we always connect to the specific window we're working with, and Ponytail's `connectWindow` ensures these local coordinates are translated to global ones internally.

## What does this mean for users?

Dogtail handles all of this logic seamlessly, so in practical use, the user doesn't need to worry about coordinate types or window connections. In fact, the vast majority of our tests work identically in both X and Wayland sessions using the Dogtail API. When running on an X session, Dogtail will use the traditional X functions to handle input and operate as it always has.

## A long journey to 1.0

We began working on the Wayland-enabled version over five years ago (originally available in the `devel/wayland` branch). It has taken all this time to ensure the solution is robust and reliable enough to warrant a 1.0 release. This version includes all the Wayland-related developments and other changes (like the GTK4 support tweaks mentioned below) and has been extensively tested. Importantly, it is backward compatible with the entire Dogtail API that has been available so far. This release includes all modules from the 0.9.x series, most notably the "procedural" module, which we plan to deprecate in favor of a completely "tree-based" approach in Dogtail 2.0.

That release will also involve significant cleanup, major code refactoring, and a transition from `pyatspi` to directly introspected `atspi`. It will also contain up date code examples and dogtail's unittests should pass with gitlab pipelines re-enabled.

For more details on these upcoming changes, see issue #29.

## 1.0+ Important: Handling GTK4 Application Windows in Dogtail

For GTK4 applications, disabling window shadows is essential to ensure accurate positioning by Dogtail. With shadows disabled, we encounters a consistent coordinate offset, which we've preconfigured as `dogtail.config.gtk4Offset`. In case of working with fullscreen windows, the offset is 0, and we manage to detect that
on-the-fly both in x11 and wayland sessions. However this process requires `python-xlib`, even for Wayland sessions, leveraging Xwayland to ascertain resolution information, as no more direct method we've found currently available for Wayland.

When window shadows are active, the perceived offset can vary significantly, influenced by factors such as the specific application, window size, and scaling settings. To ensure consistent behavior across applications, disabling shadows is recommended.

Disabling Shadows in GTK4:

To disable window shadows, add the following CSS to your GTK4 configuration (`~/.config/gtk-4.0/gtk.css`):

window, .popover, .tooltip {
    box-shadow: none;
}



Installation
============
Dogtail is available with PIP! (1.0 inclusion pending). If you'd like to use it with Wayland GNOME,
you also need to get the dogtail-ponytail-daemon: https://gitlab.gnome.org/ofourdan/gnome-ponytail-daemon
We do not have that as DEP in PIP as it compiles C code.
- todo Complete info of getting it from copr and compiling with meson

Check your distro for packages! If not at the latest version, we also have
relased tarballs for download: https://gitlab.com/dogtail/dogtail/tree/released

For details see INSTALL file.

Dependencies
============

Python bindings for your distribution, e.g. python-apt or rpm-python

PyGObject and GNOME-Python

Applications to test, e.g. from the GNOME desktop:
    http://gnome.org/


Using
=====

Currently GNOME and GTK+ applications are supported. Both Xorg and Wayland sessions.
See examples for direct dogtail use or check: https://fedoramagazine.org/automation-through-accessibility/

If you are using KDE instead, set QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1 when launching the respective program. (You can put 'export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1' to your profile file). Depending on the version, QT_ACCESSIBILITY=1 may be needed instead.

For very old KDE/QT versions (approximately 4.8.3 to 5.0), you have to install the 'qt-at-spi' QT plugin and set the environment variable QT_ACCESSIBILITY to 1.

First, enable accessibility support in your GNOME session with:
  gsettings set org.gnome.desktop.interface toolkit-accessibility true
This only affects newly-started applications, so you may want to log out and
log back in again.

Should you run "sniff" first, or be using 'dogtail-run-headless-next' or 'qecore-headless'
scripts to handle your sessions, the accessibility will be auto enabled for you.


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

We have deprecated our mailing lists as well as IRC channel. Please use our GITLAB for issues and merge requests! (Or possibly https://github.com/vhumpa/dogtail perhaps for your pull requests should
you prefer to use github, but gitlab.com is preferred)

-----

    News summary - for details see NEWS

    September-6-2024 
    
    dogtail 1.0.1

    Rebased with a number of contributions that were done to the master branch while we were working on Wayland and we have accidentaly not included them in 1.0.
    See https://gitlab.com/dogtail/dogtail/-/issues/31 
    Also returned couple of modules we thought were of no use (tc, wrapped) but were proved otherwise to keep 1.0 fully compatible with 0.x.

    August-20-2024

    Dogtail 1.0 - Wayland enabled release after 5 years of prep and testing! See the top of the page.

    November-9-2018

    A number of fixes related mainly to python3 and bilingual nature of dogtail.
    Scripts (sniff and scripts/) get /usr/bin/python3 shebangs, so distros can
    consider splitting those to subpackage.

    Note: Wayland (on gnome) support is likely coming in the next release!

    May-1-2017

    Releasing Dogtail 0.9.10

    There has been a good deal of fixes and improvements since last year's release. We're not really ready for 1.0
    yet, which is why we release this important cumulative release as 0.9.10. We have also moved our homesite to
    gitlab (fedoraproject has been discontinued). For the list of changes, simply go to:
    https://gitlab.com/dogtail/dogtail/commits/master

    Jan-18-2016

    Dogtail 0.9.9 is out!

    We're happy to announce the next release of dogtail and a pre-release for 1.0! 0.9.9 contains a big number of fixes and changes done since 0.9.0. Most important of these is framework's compatibility with Python 3. We've modified the code everywhere to run with both Python 2.7 and 3.3+. This means that from now on we maintain the same code-base and are releasing the same tarball, which can be used to package both py2 and py3 installations downstream. Just run setup.py with your favorite Python.

    Though we call this a pre-release, don't worry! 0.9.9 is considered stable and have gone through some rigorous testing already. Thanks to newly extended unit-test-set, it is actually the most self-tested release so far. For 1.0 we plan mainly to do a major module code-cleanup and we plan to finally sync it with a modern best practices howto and a new user tutorial!
    Next, python3 compatible version is coming

    Dec-08-2015

    We have accumulated a good number of enhancements since the last version, and are also working on making our first python3 ready release. All from one single code base. See ​https://fedorahosted.org/dogtail/ticket/63
    Dogtail 0.9.0 is out!

    Over the last year we've made a good number of fixes, added some new features and got overall stability to the point where we can make a new 'major minor' release. With 0.9 we're finally getting only a step away from what we'd like to get done with 1.0. Also thanks to you all who helped us out by sending patches. For details on what's new, check the ​NEWS.

    Also, if looking for offline api docs, you can download the latest ​here
    Dogtail 0.8.2 is out!

    Second update to the 0.8 series containing several fixes and improvements (notably new dogtail-run-headless-next) is out. Check ​NEWS
    Dogtail 0.8.1 is out

    A first update to the 0.8.x branch is out, containing several fixes as well as some sniff improvements.
    Dogtail 0.8.0 Final is out!

    See what's new: ​NEWS!

        Dogtail 0.8.0 Release Candidate is out!
        After more then two years a 0.7.x branch update containing several fixes, version 0.7.1, is now out!
        Thanks to ​qt-at-spi project, QT can now be used with dogtail!

    What is it?

    dogtail is a GUI test tool and automation framework written in ​Python. It uses Accessibility (a11y) technologies to communicate with desktop applications. dogtail scripts are written in Python and executed like any other Python program.
    Features

        It's Just Python™: If you can do it in Python, you can do it with dogtail.
        Object-Oriented API: With the object oriented API, you are under control of the UI tree and its elements, allowing you to write sophisticated scripts utilizing benefits of OO right deep from dogtail.
        Procedural API: However ace programmer credentials are not necessary to write useful automated scripts with procedural API.
        Easily Extensible: dogtail is object oriented "under the covers" so more advanced users can write custom classes and helper libraries easily.
        Results and debug reporting: Separate logs for test case comparisons and debug information mean less messing around for you.
        AT-SPI browser: Digging through the often-cluttered hierarchy of AT-SPI objects can be tedious. Our browser, Sniff, makes it easier.

    How do I get it?

    With the release of Gnome 3, at-spi a11y has been rewritten as well as Gtk2 moved on to Gtk3. This called for porting dogtail to use the updated technologies currently unsupported by the 0.7.1 version. Thus we worked on a new 0.8 branch which is fully compatible with the new systems. More than that - thanks to qt-at-spi - from 0.8.0 onward dogtail doesn't limit itself only to GNOME/GTK applications and can be used with KDE/QT apps as well! So, for your distribution what release to get? It's simple:
    Dogtail 0.8.x forward - for "GNOME 3 systems" or "KDE4.8+ systems"

    For Fedora 15+, Ubuntu 11.04+ or simply all systems with Gnome 3 - get dogtail 0.9.0.

    If you use Fedora you can simply do:

    yum install dogtail

    If you use RHEL7/Centos or some other Red Hat based system, you can try the latest distribution-less rpm from over ​here or, you can use the EL7 epel.

    If you don't use Fedora, just grab the latest tarball from: ​https://fedorahosted.org/released/dogtail/
    Dogtail 0.7.x - for "Gnome 2 systems"

    For all Fedora releases until 14, RHEL6, CentOS6, pre-Unity Ubuntu or simply all systems still having Gnome 2 - get version 0.7.1.1:

    If you use Fedora, have RHEL ​Epel etc., you can simply do:

    yum install dogtail

    Or you can download the latest released tarball: ​dogtail-0.7.1.1.tar.gz
    Git repository

    If you want to check out our source code repository, do:

    git clone git://git.fedorahosted.org/git/dogtail.git

    How do I use it?

    dogtail exposes elements on your desktop in a hierarchical interface. That is, you'll be working with a tree of objects like this:

        main
            gnome-panel
                Top Panel
                Bottom Panel
            xchat-gnome
                Freenode: #dogtail

    A useful tool for writing dogtail scripts is Sniff (/usr/bin/sniff or "AT-SPI Browser" in your menu), a graphical browser of that hierarchy written using dogtail.

    screenshot of sniff

    You may also want to look at the dogtail recorder (/usr/bin/dogtail-recorder or "Dogtail Script Recorder" in your menu; only in 0.7.x for now), which can actually do much of the work of script writing for you.

    If you're familiar with Python, you may want to start with the ​dogtail.tree module - specifically, dogtail.tree.root.

    If you are new to Python and/or programming in general, you may want to look at ​The Python Tutorial and the dogtail.procedural module.

    And then, there's always the ​example scripts.
    API Documentation

    dogtail's API tries to be ​self-documented, but also uses ​docstrings whenever possible. If you prefer to read your documentation in a web browser, head over to the ​HTML API docs (​tarball) for 0.8.x forward and ​here for 0.7.x branch.

    NOTE: We try to keep compatible, thus so far the only change between GNOME2-ish and GNOME3-ish branches on the side of API provided is that ​tree.doAction has been renamed to ​tree.doActionNamed
