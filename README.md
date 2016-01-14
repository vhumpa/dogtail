dogtail is a GUI test tool and automation framework written in Python. It uses Accessibility (a11y) technologies to communicate with desktop applications. dogtail scripts are written in Python and executed like any other Python program.


News
====

See NEWS file.


Installation
============

See INSTALL file.


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
    https://fedorahosted.org/dogtail/newticket


Contact
=======

Website:
    http://dogtail.fedorahosted.org/

API Documentation:
    http://fedorapeople.org/~vhumpa/dogtail/epydoc/

IRC:
    #dogtail on irc.freenode.net

Mailing list for users:
    dogtail-list@gnome.org

Mailing list for developers:
    dogtail-devel-list@gnome.org

