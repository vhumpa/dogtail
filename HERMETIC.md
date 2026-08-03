# Hermetic sessions

Run AT-SPI UI tests against a GTK app with no desktop session at all. Each test
boots its own D-Bus, its own a11y bus, its own `mutter`, then throws them away.
Nothing is borrowed from the machine you're on, and gnome-shell, a display
manager and PipeWire are all out of the picture. Works on a CI box with no
graphics session.

`dogtail-headless` logs a real desktop in via gdm. `HermeticSession` boots a
compositor instead.

## Your first test

This is `tests/test_hermetic_gtk3.py`, trimmed. It runs today.

```python
import os
import sys
import unittest
from time import sleep

from dogtail.hermetic.session import HermeticSession, dump_tree, missing_binaries

APPLICATION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hermetic_app_gtk3.py")
MISSING_BINARIES = missing_binaries()


@unittest.skipIf(MISSING_BINARIES, f"Skipping, missing: {', '.join(MISSING_BINARIES)}.")
class TestMyApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = HermeticSession()
        cls.session.boot()

    @classmethod
    def tearDownClass(cls):
        cls.session.teardown()

    def setUp(self):
        process = self.session.launch([sys.executable, APPLICATION_PATH])
        self.addCleanup(process.wait, 5)      # cleanups run last-first, so this
        self.addCleanup(process.terminate)    # waits on the terminate below it
        self.app = self.session.wait_for_app("hermetic_app_gtk3")

    def test_button_does_something(self):
        self.app.child("click me").doActionNamed("click")
        sleep(1)
        self.assertTrue(
            any(c.name == "clicked"
                for c in self.app.findChildren(lambda n: n.roleName == "label")),
            f"label never changed:\n{dump_tree(self.app)}",
        )
```

Run it like any other test in this repo:

```
python3 -m unittest tests.test_hermetic_gtk3 -v
```

`boot()` sets `os.environ` for you, so `import dogtail.tree` afterward binds to
the right bus. `launch()` sets `GDK_BACKEND=wayland`. `wait_for_app()` blocks
until the app is on the bus with a non-empty tree, and tells you why if it
never turns up.

## With pytest

There's a fixture. Put this in your `conftest.py`:

```python
from dogtail.hermetic.fixtures import hermetic_session  # noqa: F401
```

and take it as an argument:

```python
def test_button_does_something(hermetic_session):
    hermetic_session.launch([sys.executable, APPLICATION_PATH])
    app = hermetic_session.wait_for_app("hermetic_app_gtk3")
    app.child("click me").doActionNamed("click")
```

It is session-scoped, and it has to be. pytest runs every module in one
process, so a module-scoped fixture would boot a second session and hit rule 1
below. Importing `dogtail.hermetic` on its own never imports pytest, so pytest
stays a dependency of your test suite and not of dogtail.

## GTK3 and GTK4

Both work, and both are tested: `tests/test_hermetic_gtk3.py` and
`tests/test_hermetic_gtk4.py`, against `hermetic_app_gtk3.py` and
`hermetic_app_gtk4.py`. Run them in separate processes, one session per process
being rule 1 below.

The toolkit is a property of the app subprocess only. The test runner itself
stays on GTK3 either way, because `dogtail.rawinput` pins Gdk 3.0 and uses
`Gdk.Keymap`, which GTK4 dropped. Nothing in `dogtail.hermetic` cares which
toolkit the app under test uses.

One difference is worth knowing, because it will bite a `child()` lookup: GTK4
puts a label inside the button carrying the same name, GTK3 doesn't.

```
GTK3   'click me'/button
GTK4   'click me'/button, 'click me'/label
```

So `app.child("click me")` is ambiguous on GTK4 and returns whichever the tree
walk reaches first. Pin the role:

```python
app.child("click me", roleName="button")
```

## The rules

Four of them. Break one and you get a silent wrong answer instead of an error,
which is why each one has a guard or a canary behind it.

### 1. One session per process

libatspi caches its desktop connection in C the first time anything touches
it. Boot a second session in the same process and it hands you the first
one's dead objects, reporting `childCount=-1` and raising nothing.

There's no way to reset it from Python. One session per process, forever. Put
one session in `setUpClass` and restart the app between tests instead, that's
cheap and it works. A second `boot()` now raises immediately instead of lying
to you.

### 2. `doActionNamed()` first, always

```python
node.doActionNamed("click")   # good, no coordinates involved
node.click()                  # needs coordinates. see rule 3.
```

`doActionNamed` invokes the widget through AT-SPI, which skips the pointer,
the window placement and the coordinate math entirely. It's the default, and it
covers menus, dialogs, buttons and checkboxes.

### 3. Coordinates only work on a fullscreen window

A Wayland client is never told where the compositor put it. GTK thinks it's
at `(0,0)`, AT-SPI repeats that, and every widget position you read is
window-local. Injected clicks are screen-global. The two only agree when the
window fills the monitor.

Here's the problem in one dump, two windows, both claiming the origin:

```
frame:  'GNU Image Manipulation Program'  extents=(0, 0, 852, 689)
dialog: 'Welcome to GIMP 3.3.1'          extents=(0, 0, 661, 741)
```

Without gnome-shell's `Introspect` nothing knows the real positions, so the
only way round it is to avoid the situation. Fullscreen the window and the two
coordinate spaces become the same numbers:

```python
self.session.install_input()          # arms the guard
self.session.fullscreen(self.app)     # drives the app's View > Fullscreen
self.app.child("click me").click()    # now lands where you think
```

Click by coordinates on a window that isn't fullscreen and you get
`CoordinatesUnavailable` instead of a click landing in the wrong place.
Dialogs are their own windows and are never fullscreen, so use
`doActionNamed` on those.

An app with no fullscreen menu item doesn't get coordinate clicking at all.
`doActionNamed` still works.

### 4. Real input needs `install_input()`

```python
self.session.install_input()
```

This points dogtail's input at this session's mutter and arms the coordinate
guard. Skip it and `click()`/`type_text()` go nowhere.

## What works

| | |
|---|---|
| menus, dialogs, buttons, checkboxes | yes, via `doActionNamed` |
| reading state: titles, labels, text, tree | yes |
| typing (`type_text`) | yes, after `install_input()` |
| clicking by coordinate (`node.click()`) | only on a fullscreen window |
| canvas / drag / click-by-position | only on a fullscreen window |
| dialogs by coordinate | no, use `doActionNamed` |
| screenshots | no, use `dump_tree(node)`, diffs better in CI anyway |
| video, XPath, touch, scroll, KWin, sway | no |

## When it breaks

Everything in this stack fails quietly, so match the symptom:

| Symptom | Cause | Fix |
|---|---|---|
| `childCount=-1`, empty desktop | second session in one process | one session per process (rule 1) |
| app registers, tree is empty | ATK bridge off | `NO_AT_BRIDGE=1` in the env, or `at-spi2-atk` missing |
| `CoordinatesUnavailable` | window not fullscreen | `doActionNamed`, or `session.fullscreen(app)` (rule 3) |
| click does nothing, no error | injection not installed | `session.install_input()` (rule 4) |
| first click of a session lost | mutter drops startup events | raise `$DOGTAIL_WARM_UP_EVENTS` above 6 |
| `timed out waiting for ...` | slow box, or the process died | the error carries the log tail. if the box is just loaded, raise `$DOGTAIL_HERMETIC_TIMEOUT` |
| `at-spi2-registryd not found` | distro puts it elsewhere | set `$DOGTAIL_REGISTRYD` |

`dump_tree(node)` prints the whole AT-SPI tree. Put it in assertion messages.
It's what you use instead of a screenshot, and it costs nothing.

## Knobs

Three environment variables, all optional:

| Variable | Default | What it does |
|---|---|---|
| `DOGTAIL_HERMETIC_TIMEOUT` | `10` | Seconds to wait for the bus, registryd, mutter and fullscreen. `wait_for_app` gets 3x it. Raise it on a loaded CI runner. |
| `DOGTAIL_WARM_UP_EVENTS` | `6` | Pointer events burned at session start while mutter's virtual devices come up. It drops them silently, so an undercount costs you the first click and nothing else. |
| `DOGTAIL_REGISTRYD` | first hit in `REGISTRYD_PATHS` | Where `at-spi2-registryd` lives. It is not on `$PATH` anywhere, so it gets looked for at the three known distro locations; set this if yours is a fourth. |

The warm-up count was measured against mutter 50.x. Boot on a different major
and you get a warning saying so, because there is no readiness signal to wait
on and mutter moves quickly.

## Requirements

`mutter`, `dbus-daemon`, `dbus-send` and `at-spi2-registryd`, all of which the
session finds on its own. It needs none of gnome-shell, PipeWire, a display
manager or X.

`boot()` checks for all four before it starts anything and names whatever is
missing. `missing_binaries()` returns the same list without booting, which is
what to hang a `skipIf` on:

```python
from dogtail.hermetic.session import missing_binaries

MISSING_BINARIES = missing_binaries()

@unittest.skipIf(MISSING_BINARIES, f"Skipping, missing: {', '.join(MISSING_BINARIES)}.")
class TestMyApp(unittest.TestCase):
    ...
```

## How it works

Boot order matters and is enforced:

```
dbus-daemon -> at-spi2-registryd -> wait for org.a11y.atspi.Registry
            -> mutter --headless --virtual-monitor -> wait for its bus names -> app
```

`XDG_*` all point at a tempdir, so the app under test reads none of your
config and leaves nothing behind. Input goes over
`org.gnome.Mutter.RemoteDesktop`, without ScreenCast or PipeWire.

Absolute pointer motion needs a stream (and so PipeWire), so the first move of
a session slams into the top-left corner, which clamps to `(0,0)`, then moves
relative from there. Every move after that is a plain delta from the last known
position. Slamming again mid-gesture would drag the held button through the
corner and back, which on a canvas paints exactly what it sounds like.

dogtail has no backend seam, but everything funnels through the
`PonytailHelper` singleton, so `install_input()` swaps our object into it and
`rawinput.py` stays untouched.
