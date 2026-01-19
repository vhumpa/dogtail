#!/usr/bin/python3
"""
Unit tests for the dogtail.rawinput.
"""

# pylint: disable=import-outside-toplevel

import unittest
from dogtail.rawinput import (
    absolute_motion,
    absolute_motion_with_trajectory,
    check_coordinates,
    click,
    double_click,
    press,
    release,
)


class TestRawinput(unittest.TestCase):
    """
    Class to test dogtail's rawinput.
    """

    def test_absolute_motion(self):
        """
        Testing absolute_motion.
        """

        absolute_motion(50, 50)
        absolute_motion(100, 100)
        absolute_motion(150, 150)
        absolute_motion(200, 200)
        absolute_motion(200, 200, mouse_delay=1)
        absolute_motion(200, 200, mouse_delay=1, check=True)
        absolute_motion(-200, -200, mouse_delay=1, check=False)

    def test_motion_with_trajectory(self):
        """
        Testing absolute_motion_with_trajectory.
        """

        absolute_motion_with_trajectory(100, 100, 110, 110)
        absolute_motion_with_trajectory(110, 110, 120, 120)
        absolute_motion_with_trajectory(120, 120, 130, 130)
        absolute_motion_with_trajectory(130, 130, 150, 150, mouse_delay=0.1)

    def test_check_coordinates_directly(self):
        """
        Testing check_coordinates directly.
        """

        check_coordinates(0, 0)
        check_coordinates(-0, -0)
        check_coordinates(10, 0)
        check_coordinates(0, 10)

        # There are shadows which can be in negative, but that does not mean a bug.
        # We set the limits to (-50,-50), most issues are way over this value.
        with self.assertRaises(ValueError):
            check_coordinates(-100, 100)

        with self.assertRaises(ValueError):
            check_coordinates(100, -100)

        with self.assertRaises(ValueError):
            check_coordinates(-100, -100)

    def test_check_coordinates_in_methods(self):
        """
        Testing check_coordinates in methods.
        """

        # There are shadows which can be in negative, but that does not mean a bug.
        # We set the limits to (-50,-50), most issues are way over this value.

        # Absolute Motion.
        with self.assertRaises(ValueError):
            absolute_motion(-100, 100)
        with self.assertRaises(ValueError):
            absolute_motion(100, -100)
        with self.assertRaises(ValueError):
            absolute_motion(-100, -100)

        # Absolute Motion With Trajectory.
        with self.assertRaises(ValueError):
            absolute_motion_with_trajectory(-100, 100, 100, 100)
        with self.assertRaises(ValueError):
            absolute_motion_with_trajectory(100, -100, 100, 100)
        with self.assertRaises(ValueError):
            absolute_motion_with_trajectory(100, 100, -100, 100)
        with self.assertRaises(ValueError):
            absolute_motion_with_trajectory(100, 100, 100, -100)

        # Click.
        with self.assertRaises(ValueError):
            click(-100, 100)
        with self.assertRaises(ValueError):
            click(100, -100)
        with self.assertRaises(ValueError):
            click(-100, -100)

        # Double Click.
        with self.assertRaises(ValueError):
            double_click(-100, 100)
        with self.assertRaises(ValueError):
            double_click(100, -100)
        with self.assertRaises(ValueError):
            double_click(-100, -100)

        # Press.
        with self.assertRaises(ValueError):
            press(-100, 100)
        with self.assertRaises(ValueError):
            press(100, -100)
        with self.assertRaises(ValueError):
            press(-100, -100)

        # Release.
        with self.assertRaises(ValueError):
            release(-100, 100)
        with self.assertRaises(ValueError):
            release(100, -100)
        with self.assertRaises(ValueError):
            release(-100, -100)


if __name__ == "__main__":
    unittest.main()
