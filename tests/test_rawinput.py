#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import dogtail.config
import pyatspi
from dogtail.rawinput import absoluteMotion, relativeMotion, doubleClick, press, drag, dragWithTrajectory, \
    pressKey, absoluteMotionWithTrajectory, release, checkCoordinates, click, keyCombo, typeText
from dogtail.tree import SearchError
from gtkdemotest import GtkDemoTest

dogtail.config.config.logDebugToFile = False
dogtail.config.config.logDebugToStdOut = True

"""
Unit tests for the dogtail.rawinput package
"""


class TestRawinput(GtkDemoTest):

    def test_motion(self):
        absoluteMotion(100, 100)
        absoluteMotion(100, 100, mouseDelay=1)
        absoluteMotion(-100, -100, check=False)
        absoluteMotion(100, 100, mouseDelay=1, check=False)
        relativeMotion(-10, -10)
        absoluteMotion(100, 100)
        relativeMotion(-10, -10, mouseDelay=1)

    def test_motion_with_trajectory(self):
        absoluteMotionWithTrajectory(100, 100, 120, 120)
        absoluteMotionWithTrajectory(120, 120, 120, 120)
        absoluteMotionWithTrajectory(120, 120, 130, 120)
        absoluteMotionWithTrajectory(130, 120, 130, 130)
        absoluteMotionWithTrajectory(130, 130, 150, 100, mouseDelay=0.1)

    def test_check_coordinates_direct(self):
        checkCoordinates(0, 0)
        checkCoordinates(-0, -0)
        checkCoordinates(0, 10)
        checkCoordinates(10, 0)
        with self.assertRaises(ValueError):
            checkCoordinates(-1, 100)
        with self.assertRaises(ValueError):
            checkCoordinates(100, -1)
        with self.assertRaises(ValueError):
            checkCoordinates(-1, -1)

    def test_check_coordinates_builtin(self):
        with self.assertRaises(ValueError):
            absoluteMotion(-5, 5)
        with self.assertRaises(ValueError):
            absoluteMotion(5, -5)
        with self.assertRaises(ValueError):
            absoluteMotionWithTrajectory(10, 10, -5, 5)
        with self.assertRaises(ValueError):
            absoluteMotionWithTrajectory(10, 10, 5, -5)
        with self.assertRaises(ValueError):
            absoluteMotionWithTrajectory(-5, 5, 10, 10)
        with self.assertRaises(ValueError):
            absoluteMotionWithTrajectory(5, -5, 10, 10)
        with self.assertRaises(ValueError):
            click(-5, 5)
        with self.assertRaises(ValueError):
            click(5, -5)
        with self.assertRaises(ValueError):
            doubleClick(-5, 5)
        with self.assertRaises(ValueError):
            doubleClick(5, -5)
        with self.assertRaises(ValueError):
            press(-5, 5)
        with self.assertRaises(ValueError):
            press(5, -5)
        with self.assertRaises(ValueError):
            release(-5, 5)
        with self.assertRaises(ValueError):
            release(5, -5)

    def test_doubleClick(self):
        btn = self.app.child('Builder')
        doubleClick(btn.position[0], btn.position[1])
        self.assertEqual(len([x for x in self.app.children if x.name in ['GtkBuilder demo', 'Builder']]), 2)

    def test_click(self):
        btn = self.app.child('Builder')
        self.assertFalse(btn.focused)
        click(btn.position[0], btn.position[1])
        self.assertTrue(btn.focused)

    def test_press_release(self):
        self.runDemo('Builder')
        try:
            wnd = self.app.child('GtkBuilder demo', roleName='frame', recursive=False, retry=False)
        except dogtail.tree.SearchError:
            wnd = self.app.child('Builder', roleName='frame', recursive=False, retry=False)
        btn = wnd.button('New')
        press(btn.position[0] + btn.size[0] / 2, btn.position[1] + btn.size[1] / 2, check=False)
        self.assertIn(pyatspi.STATE_ARMED, btn.getState().getStates())
        release(btn.position[0] + btn.size[0] / 2, btn.position[1] + btn.size[1] / 2, check=False)
        self.assertNotIn(pyatspi.STATE_ARMED, btn.getState().getStates())

    def test_drag(self):
        self.runDemo('Tool Palette')
        win = self.app.window('Tool Palette')
        src = win.findChildren(lambda x: x.roleName == 'push button' and x.showing)[0]
        dst = win.child(roleName='viewport')
        drag((src.position[0] + src.size[0] / 2, src.position[1] + src.size[1] / 2),
             (dst.position[0] + dst.size[0] / 2, dst.position[1] + dst.size[1] / 2))

    def test_drag_with_trajectory(self):
        self.runDemo('Tool Palette')
        win = self.app.window('Tool Palette')
        src = win.findChildren(lambda x: x.roleName == 'push button' and x.showing)[0]
        dst = win.child(roleName='viewport')
        dragWithTrajectory((src.position[0] + src.size[0] / 2, src.position[1] + src.size[1] / 2),
                           (dst.position[0] + dst.size[0] / 2, dst.position[1] + dst.size[1] / 2))

    def test_pressKey_no_such_key(self):
        with self.assertRaises(KeyError):
            pressKey("no such key")

    def test_keyCombo_simple(self):
        keyCombo('<End>')
        self.assertTrue(self.app.child('Tree View').showing)

    def test_keyCombo_multi(self):
        self.runDemo('Clipboard')
        try:
            wnd = self.app.child('Clipboard demo', roleName='frame', retry=False, recursive=False)
        except SearchError:
            wnd = self.app.child('Clipboard', roleName='frame', retry=False, recursive=False)
        textfield = wnd.child(roleName='text')
        textfield.text = 'something'
        keyCombo('<Control>a')
        keyCombo('<Control>c')
        keyCombo('<Control>v')
        keyCombo('<Control>v')
        self.assertEqual(textfield.text, 'somethingsomething')

    def test_keyCombo_wrong_key(self):
        with self.assertRaises(ValueError):
            keyCombo('<WORK_FASTER_THAN_LIGHTSPEED>')

    def test_typeText(self):
        self.runDemo('Clipboard')
        try:
            wnd = self.app.child('Clipboard demo', roleName='frame', retry=False, recursive=False)
        except SearchError:
            wnd = self.app.child('Clipboard', roleName='frame', retry=False, recursive=False)
        textfield = wnd.child(roleName='text')
        typeText('something')
        self.assertEqual(textfield.text, 'something')
