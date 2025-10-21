# pylint: disable=import-outside-toplevel

import os
import unittest
from time import sleep

from dogtail.tree import root
from dogtail.rawinput import (
    drag,
    drag_with_trajectory,
    press_key,
)
from dogtail.logging import logging_class
LOGGING = logging_class.logger



class TestGnomeShellOverviewRawinput(unittest.TestCase):
    """
    Class to test dogtail's rawinput drag methods.
    """

    # Skipping for now, breaking testing-farm somehow, probably too many events generated?
    #@unittest.SkipTest
    def test_drag_in_overview(self):

        """
        Testing drag.
        """

        press_key("Esc")
        sleep(1)

        os.system("killall nautilus > /dev/null 2>&1")

        gnome_shell = root.application("gnome-shell")

        print("This test assumes Nautilus - Files to be Pinned")
        os.system("gsettings set org.gnome.shell favorite-apps \"['org.gnome.Nautilus.desktop']\"")
        sleep(1)

        press_key("Esc")
        sleep(1)
        press_key("Super")
        sleep(1)

        # Search for Files - assuming Files are Pinned.
        file_button = gnome_shell.find_child(
            lambda x: x.name == "Files" and x.role_name in ("button", "push button")
        )

        start_run_button_x = file_button.center[0]
        start_run_button_y = file_button.center[1]

        # SHould be enough, lets not assume resolution.
        end_run_button_x = 300
        end_run_button_y = 300

        drag(
            (start_run_button_x, start_run_button_y),
            (end_run_button_x, end_run_button_y),
        )

        self.assertTrue("org.gnome.Nautilus" in [x.name for x in root.applications()])
        os.system("killall nautilus > /dev/null 2>&1")
        press_key("Esc")


    def test_drag_with_trajectory_in_overview(self):
        """
        Testing drag with trajectory.
        """

        press_key("Esc")
        sleep(1)

        os.system("killall nautilus > /dev/null 2>&1")

        gnome_shell = root.application("gnome-shell")

        print("This test assumes Nautilus - Files to be Pinned")
        os.system("gsettings set org.gnome.shell favorite-apps \"['org.gnome.Nautilus.desktop']\"")
        sleep(1)

        press_key("Esc")
        sleep(1)
        press_key("Super")
        sleep(1)

        # Search for Files - assuming Files are Pinned.
        file_button = gnome_shell.find_child(
            lambda x: x.name == "Files" and x.role_name in ("button", "push button")
        )

        start_run_button_x = file_button.center[0]
        start_run_button_y = file_button.center[1]

        # SHould be enough, lets not assume resolution.
        end_run_button_x = 300
        end_run_button_y = 300

        drag_with_trajectory(
            (start_run_button_x, start_run_button_y),
            (end_run_button_x, end_run_button_y),
            mouse_delay=0.02
        )

        self.assertTrue("org.gnome.Nautilus" in [x.name for x in root.applications()])
        os.system("killall nautilus > /dev/null 2>&1")
        press_key("Esc")


if __name__ == "__main__":
    unittest.main()