# Hermetic sessions

Run AT-SPI UI tests against a GTK app with no desktop session at all. Each test
boots its own D-Bus, its own a11y bus, its own `mutter`, then throws them away.
No gnome-shell, no display manager, no PipeWire, nothing borrowed from the
machine you're on. Works on a CI box with no graphics session.

This isn't `dogtail-headless`, which logs a real desktop in via gdm.
`dogtail-headless` boots a desktop. `HermeticSession` boots a compositor.

## Your first test

This is `tests/test_hermetic_gtk3.py`, trimmed. It runs today.

```python
import os, shutil, sys, unittest
from time import sleep
from dogtail.hermetic.session import HermeticSession, dump_tree

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hermetic_app_gtk3.py")


@unittest.skipIf(not shutil.which("mutter"), "Skipping, no mutter.")
class TestMyApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = HermeticSession()
        cls.session.boot()

    @classmethod
    def tearDownClass(cls):
        cls.session.teardown()

    def setUp(self):
        process = self.session.launch([sys.executable, APP])
        self.addCleanup(process.terminate)
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

`doActionNamed` invokes the widget through AT-SPI. No pointer, no window
placement, no coordinate math, nothing to get wrong. It's the default for a
reason, and it covers menus, dialogs, buttons, checkboxes.

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

Without gnome-shell's `Introspect` nothing knows the real positions, so this
isn't fixable, only avoidable. Fullscreen the window and the two coordinate
spaces become the same numbers:

```python
self.session.install_input()          # arms the guard
self.session.fullscreen(self.app)     # drives the app's View > Fullscreen
self.app.child("click me").click()    # now lands where you think
```

Click by coordinates on a window that isn't fullscreen and you get
`CoordinatesUnavailable` instead of a click landing in the wrong place.
Dialogs are their own windows and are never fullscreen, so use
`doActionNamed` on those.

An app with no fullscreen menu item doesn't get coordinate clicking. That's
the honest answer. `doActionNamed` still works.

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
| first click of a session lost | mutter drops startup events | already handled, if it comes back, raise `WARM_UP_EVENTS` in `mutter.py` |
| `timed out waiting for D-Bus name` | mutter or registryd died | the error carries their log tail, read it |
| `at-spi2-registryd not found` | distro puts it elsewhere | set `$DOGTAIL_REGISTRYD` |

`dump_tree(node)` prints the whole AT-SPI tree. Put it in assertion messages,
it's the screenshot replacement and it costs nothing.

## Requirements

`mutter` and `at-spi2-registryd`, both of which the sessions find on their
own. No gnome-shell, no PipeWire, no display manager, no X.

## How it works

Boot order matters and is enforced:

```
dbus-daemon -> at-spi2-registryd -> wait for org.a11y.atspi.Registry
            -> mutter --headless --virtual-monitor -> wait for its bus names -> app
```

`XDG_*` all point at a tempdir, so the app under test reads none of your
config and leaves nothing behind. Input goes over
`org.gnome.Mutter.RemoteDesktop`, no ScreenCast, no PipeWire. Absolute pointer
motion needs a stream (and so PipeWire), so a move is a slam into the
top-left corner, which clamps to `(0,0)`, plus a relative move from there.

dogtail has no backend seam, but everything funnels through the
`PonytailHelper` singleton, so `install_input()` swaps our object into it and
`rawinput.py` stays untouched.
