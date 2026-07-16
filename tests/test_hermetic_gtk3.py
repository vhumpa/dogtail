#!/usr/bin/python3
"""
Tests for dogtail.hermetic, a private mutter session with no gnome-shell.

One session serves the whole class, since libatspi will not let a process have
two. The application can be restarted though, so each test gets a fresh one.

The application is fullscreen on purpose: AT-SPI coordinates are window-local
while injection is screen-global, and only fullscreen makes the two agree. That
is also why doActionNamed is the default here and clicking by coordinates is not.
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position

import os
import shutil
import sys
import unittest

from time import sleep

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dogtail.hermetic.session import CoordinatesUnavailable, HermeticSession, dump_tree

APPLICATION_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "hermetic_app_gtk3.py"
)


@unittest.skipIf(not shutil.which("mutter"), "Skipping, no mutter.")
class TestHermeticGtk3(unittest.TestCase):
    """
    Class to test dogtail's hermetic session against a real GTK3 application.
    """

    session = None

    @classmethod
    def setUpClass(cls):
        """
        Boot the one session the whole class shares.
        """

        cls.session = HermeticSession()
        cls.session.boot()


    @classmethod
    def tearDownClass(cls):
        """
        Tear the session down, whatever the tests did.
        """

        if cls.session is not None:
            cls.session.teardown()


    def setUp(self):
        """
        Start a fresh application per test, as the session is shared and cannot be.
        """

        self.application = self._launch()


    def _launch(self, *arguments, application_name="hermetic_app_gtk3"):
        """
        Start the test application and wait for it on the a11y bus.

        :param arguments: Extra arguments for the application.
        :type arguments: str

        :param application_name: Name to wait for, defaults to "hermetic_app_gtk3"
        :type application_name: str, optional

        :return: The application node.
        :rtype: dogtail.tree.Node
        """

        process = self.session.launch([sys.executable, APPLICATION_PATH, *arguments])
        self.addCleanup(self._stop_application, process)

        return self.session.wait_for_app(application_name)


    def _stop_application(self, process):
        """
        Stop a test application.

        :param process: The application to stop.
        :type process: subprocess.Popen
        """

        process.terminate()
        process.wait(timeout=5)


    def _label_says(self, text):
        """
        Report whether any label in the application carries the given text.

        :param text: Text to look for.
        :type text: str

        :return: True if a label matches.
        :rtype: bool
        """

        return any(
            child.name == text
            for child in self.application.findChildren(
                lambda node: node.roleName == "label"
            )
        )


    def test_app_registered(self):
        """
        Testing that the application turns up on the private a11y bus.

        If this fails the rest of the class is noise.
        """

        self.assertIn("hermetic_app_gtk3", self.application.name)
        self.assertTrue(
            self.application.children, f"empty tree:\n{dump_tree(self.application)}"
        )


    def test_do_action_click(self):
        """
        Testing the do_action path, with no coordinates or window placement involved.
        """

        self.assertTrue(self._label_says("not clicked"))

        self.application.child("click me").doActionNamed("click")
        sleep(1)

        self.assertTrue(
            self._label_says("clicked"),
            f"label never changed:\n{dump_tree(self.application)}",
        )


    def test_real_pointer_input(self):
        """
        Testing that injected pointer events actually land.

        Worth having because do_action passes just fine with injection totally
        broken. This is also the canary for mutter dropping more startup events
        than WARM_UP_EVENTS covers.
        """

        self.session.install_input()
        self.assertTrue(self._label_says("not clicked"))

        self.application.child("click me").click()
        sleep(1)

        self.assertTrue(
            self._label_says("clicked"),
            f"real click never reached the app:\n{dump_tree(self.application)}",
        )


    def test_coordinate_guard_refuses_windowed_app(self):
        """
        Testing that the same click is refused when the application is not fullscreen.

        Refusing beats clicking whatever happens to be at those screen coordinates.
        """

        self.session.install_input()
        application = self._launch("--windowed", application_name="hermetic_app_windowed")

        with self.assertRaises(CoordinatesUnavailable) as caught:
            application.child("click me").click()

        self.assertIn("window-local", str(caught.exception))
        self.assertTrue(self._label_says("not clicked"))


    def test_real_keyboard_input(self):
        """
        Testing that keystrokes land, and that the -8 keycode offset is right.
        """

        from dogtail.rawinput import type_text

        self.session.install_input()

        entry = self.application.child(roleName="text")
        entry.click()
        sleep(0.5)

        type_text("hermetic")
        sleep(1)

        self.assertEqual(
            entry.text, "hermetic",
            f"typed text never arrived:\n{dump_tree(self.application)}",
        )


if __name__ == "__main__":
    unittest.main()
