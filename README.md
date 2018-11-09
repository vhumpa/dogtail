dogtail is a GUI test tool and automation framework written in Python. It uses Accessibility (a11y) technologies to communicate with desktop applications. dogtail scripts are written in Python and executed like any other Python program.


News
====

See NEWS file.


Installation
============

Check your distro for packages! If not at the latest version, we also have
relased tarballs for download: https://gitlab.com/dogtail/dogtail/tree/released

For details see INSTALL file.

Dependencies
============

Python bindings for your distribution, e.g. python-apt or rpm-python

PyGObject and GNOME-Python

Applications to test, e.g. from the GNOME desktop:
    http://gnome.org/

Xvfb and xinit:
    http://xorg.freedesktop.org/

Using
=====

Currently GNOME and GTK+ applications are supported. Thanks to qt-at-spi
KDE4 and QT applications are now available too.

First, enable accessibility support in your GNOME session with:
  gsettings set org.gnome.desktop.interface toolkit-accessibility true
This only affects newly-started applications, so you may want to log out and
log back in again.

Then, look at some of the example scripts. Run them, tweak them, write your own.

I suggest starting with gedit-test-utf8-procedural-api.py, as it's updated the
most often.

If you are using KDE instead, install the 'qt-at-spi' QT plugin and make sure
you QT_ACCESSIBILITY set to 1 throughout your environment (you can put
'export QT_ACCESSIBILITY=1' to your profile file). QT accessibility should
be stable from QT 4.8.3 onward.

Bugs
====

Please report any bugs at:
    https://gitlab.com/dogtail/dogtail/issues


Contact
=======

Website:
    https://gitlab.com/dogtail/dogtail/

API Documentation:
    http://fedorapeople.org/~vhumpa/dogtail/epydoc/

IRC:
    #dogtail on irc.freenode.net

Mailing list for users:
    dogtail-list@gnome.org

Mailing list for developers:
    dogtail-devel-list@gnome.org


-----

    News

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
