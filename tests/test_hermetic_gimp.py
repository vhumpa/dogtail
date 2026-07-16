#!/usr/bin/python3
"""
Tests for dogtail.hermetic against a real GIMP install - new image, new
layer, checking the window title updates ("1 layer" -> "2 layers"), and
export-to-PNG, which is the hard case: GIMP's export plugins run as their
own process and register as their own AT-SPI application, not nested under
the main "gimp" one. See test_export_png_via_separate_atspi_app.

GIMP's a11y tree is deep and menus don't have stable indices, so this uses a
small recursive find_first instead of node.child() for menu/dialog lookups.
GIMP is also not fullscreen (its own window manager decides placement), so
do_action is mandatory here - coordinate clicks would be window-local numbers
landing who knows where on the virtual monitor.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position

import os
import shutil
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogtail.hermetic.session import HermeticSession, dump_tree


def _resolve_gimp():
    """$DOGTAIL_GIMP wins, then whatever's on PATH. None means skip."""
    override = os.environ.get("DOGTAIL_GIMP")
    if override:
        return override
    return shutil.which("gimp") or shutil.which("gimp-3.3")


GIMP = _resolve_gimp()


def _gimp_extra_env(gimp_path):
    """dev builds under a custom prefix need their own libs on the path,
    /usr/bin ones are already wired up by the system linker."""
    bin_dir = os.path.dirname(os.path.abspath(gimp_path))
    if bin_dir == "/usr/bin":
        return {}
    prefix = os.path.dirname(bin_dir)
    return {"LD_LIBRARY_PATH": os.path.join(prefix, "lib")}


def find_first(node, pred, max_depth=10, depth=0):
    """menus are buried deep and node.child() wants an exact/unique match we
    don't always have mid-search, so walk the whole subtree instead."""
    try:
        if pred(node):
            return node
    except Exception:
        return None
    if depth >= max_depth:
        return None
    try:
        for child in node.children:
            found = find_first(child, pred, max_depth, depth + 1)
            if found:
                return found
    except Exception:
        pass
    return None


def wait_for(fn, timeout=15, interval=0.3):
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = fn()
        if result:
            return result
        time.sleep(interval)
    return None


@unittest.skipIf(not shutil.which("mutter"), "Skipping, no mutter.")
@unittest.skipIf(not GIMP, "Skipping, no GIMP (set $DOGTAIL_GIMP or install gimp).")
class TestHermeticGimp(unittest.TestCase):
    """
    Class to test dogtail's hermetic session against a real GIMP install.
    """

    session = None

    @classmethod
    def setUpClass(cls):
        cls.session = HermeticSession(boot_timeout=20)
        cls.session.boot()

    @classmethod
    def tearDownClass(cls):
        if cls.session is not None:
            cls.session.teardown()

    def setUp(self):
        """
        Fresh GIMP per test, the session is shared and can't be.
        """

        self.process = self.session.launch(
            [GIMP, "--no-splash", "--new-instance"],
            extra_env=_gimp_extra_env(GIMP),
        )
        self.addCleanup(self._stop_app)
        self.app = self.session.wait_for_app("gimp", timeout=60)

    def _stop_app(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except Exception:
            self.process.kill()

    def _click_menu_item(self, menu_name, item_name):
        menu = find_first(self.app, lambda n: n.roleName == "menu" and n.name == menu_name)
        self.assertIsNotNone(menu, f"menu {menu_name!r} not found:\n{dump_tree(self.app)}")
        menu.doActionNamed("click")

        item = wait_for(
            lambda: find_first(self.app, lambda n: n.roleName == "menu item" and n.name == item_name),
            timeout=5,
        )
        self.assertIsNotNone(item, f"menu item {item_name!r} not found under {menu_name!r}")
        item.doActionNamed("click")

    def _confirm_dialog(self, button_name="OK", timeout=10):
        dialog = wait_for(lambda: find_first(self.app, lambda n: n.roleName == "dialog"), timeout=timeout)
        self.assertIsNotNone(dialog, "expected dialog did not appear")
        button = find_first(dialog, lambda n: "button" in n.roleName and n.name == button_name)
        self.assertIsNotNone(button, f"dialog has no {button_name!r} button:\n{dump_tree(dialog)}")
        button.doActionNamed("click")

    def _image_window(self):
        return find_first(
            self.app,
            lambda n: n.roleName == "frame" and "GIMP" in (n.name or "") and "layer" in (n.name or ""),
        )

    def _close_welcome_dialog(self):
        welcome = wait_for(
            lambda: find_first(self.app, lambda n: n.roleName == "dialog" and "Welcome" in (n.name or "")),
            timeout=10,
        )
        if welcome:
            find_first(welcome, lambda n: n.roleName == "button" and n.name == "Close").doActionNamed("click")
            time.sleep(1)

    def test_new_layer_updates_title(self):
        """
        File > New then Layer > New Layer, window title tracks the layer
        count both times.
        """

        self._close_welcome_dialog()

        self._click_menu_item("File", "New...")
        self._confirm_dialog("OK")

        win_before = wait_for(self._image_window, timeout=10)
        self.assertIsNotNone(win_before, f"image window not found:\n{dump_tree(self.app)}")
        self.assertIn(
            "1 layer", win_before.name,
            f"expected a fresh image to report '1 layer', got: {win_before.name!r}",
        )

        self._click_menu_item("Layer", "New Layer...")
        self._confirm_dialog("OK")

        win_after = wait_for(
            lambda: self._image_window() if "2 layers" in (self._image_window().name or "") else None,
            timeout=10,
        )
        self.assertIsNotNone(
            win_after,
            f"expected '2 layers' in window title after adding a layer:\n{dump_tree(self.app)}",
        )

    def test_export_png_via_separate_atspi_app(self):
        """
        The hard case this plan flagged: GIMP's PNG export runs as its own
        process (file-png) with its own AT-SPI application, not nested under
        "gimp". Turns out that's a non-event for do_action - its dialog is
        just another application on the same bus, found and clicked the same
        way as anything under "gimp". No window/process tracking needed.
        """

        import dogtail.tree  # noqa: PLC0415 - only safe once boot() has set env

        self._close_welcome_dialog()
        self._click_menu_item("File", "New...")
        self._confirm_dialog("OK")
        wait_for(self._image_window, timeout=10)

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = os.path.join(tmp_dir, "hermetic_export.png")

            self._click_menu_item("File", "Export As...")
            chooser = wait_for(
                lambda: find_first(self.app, lambda n: n.roleName == "file chooser" and n.name == "Export Image"),
                timeout=10,
            )
            self.assertIsNotNone(chooser, f"Export Image file chooser never appeared:\n{dump_tree(self.app)}")

            name_field = find_first(chooser, lambda n: n.roleName == "text")
            name_field.text = out_path
            find_first(chooser, lambda n: "button" in n.roleName and n.name == "Export").doActionNamed("click")

            png_app = wait_for(
                lambda: next((c for c in dogtail.tree.root.children if c.name == "file-png"), None),
                timeout=10,
            )
            self.assertIsNotNone(
                png_app,
                "file-png plugin never registered its own AT-SPI application - "
                "either the plugin didn't run, or this GIMP build doesn't split "
                "exporters into a separate process",
            )

            png_dialog = find_first(png_app, lambda n: n.roleName == "dialog")
            self.assertIsNotNone(png_dialog, f"file-png registered but has no dialog:\n{dump_tree(png_app)}")
            find_first(png_dialog, lambda n: "button" in n.roleName and n.name == "Export").doActionNamed("click")

            exported = wait_for(lambda: os.path.exists(out_path) or None, timeout=10)
            self.assertTrue(exported, f"export never wrote {out_path}")
            self.assertGreater(os.path.getsize(out_path), 0, "exported PNG is empty")


if __name__ == "__main__":
    unittest.main()
