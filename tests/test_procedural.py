#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, unicode_literals
from dogtail.procedural import focus, keyCombo, deselect, activate, select, click, tree, FocusError, run, config, type
from dogtail.tree import SearchError, ActionNotSupported, NotSensitiveError
from gtkdemotest import GtkDemoTest, trap_stdout
from time import sleep
import pyatspi

"""
Unit tests for the dogtail.procedural API
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

config.logDebugToFile = False
config.logDebugToStdOut = True


class GtkDemoTest(GtkDemoTest):

    def setUp(self):
        self.pid = run('gtk3-demo')
        # Turn off activities overview
        keyCombo('Esc')
        self.app = focus.application.node
    
    def tearDown(self):
        import signal, os
        os.kill(self.pid, signal.SIGKILL)
        os.system('killall gedit > /dev/null 2>&1')


class TestFocusApplication(GtkDemoTest):

    def test_throw_exception_on_focusing_bogus_name(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.application, "should not be found")

    def test_focusing_basic(self):
        """
        Ensure that focus.application() sets focus.application.node properly
        """
        focus.application.node = None
        focus.application("gtk3-demo")
        self.assertEqual(focus.application.node, self.app)

    def test_throw_exception_on_get_no_such_attribute(self):
        with self.assertRaises(AttributeError):
            focus.no_such_attribute

    def test_throw_exception_on_get_no_such_attribute_when_node_doesnt_exist(self):
        focus.application.node = None
        with self.assertRaises(AttributeError):
            focus.no_such_attribute

    def test_throw_exception_on_set_no_such_attribute(self):
        with self.assertRaises(AttributeError):
            focus.no_such_attribute = 0


class TestFocusWindow(GtkDemoTest):

    def test_focusing_bogus_name_without_a_fatal_error(self):
        config.fatalErrors = False
        output = trap_stdout(focus.window, "should not be found")
        self.assertIsNone(focus.window.node)

    def test_throw_exception_on_focusing_bogus_name(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.window, "should not be found")


class TestFocusDialog(GtkDemoTest):

    def test_focusing_bogus_name_without_a_fatal_error(self):
        config.fatalErrors = False
        output = trap_stdout(focus.dialog, "should not be found")
        self.assertIsNone(focus.dialog.node)

    def test_throw_exception_on_focusing_bogus_name(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.dialog, "should not be found")


class TestFocusWidget(GtkDemoTest):

    def test_focusing_empty_name(self):
        self.assertRaises(TypeError, focus.widget)

    def test_focusing_bogus_name_without_a_fatal_error(self):
        config.fatalErrors = False
        output = trap_stdout(focus.widget, "should not be found")
        self.assertIsNone(focus.widget.node)

    def test_throw_exception_on_focusing_bogus_name(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.widget, "should not be found")

    def test_focusing_basic(self):
        """
        Ensure that focus.widget('foo') finds a node with name 'foo'
        """
        focus.widget("Application Class")
        self.assertEqual(focus.widget.name, "Application Class")


class TestFocus(GtkDemoTest):

    def test_initial_state(self):
        """
        Ensure that focus.widget, focus.dialog and focus.window are None initially.
        """
        self.assertIsNone(focus.widget.node)
        self.assertIsNone(focus.dialog.node)
        self.assertIsNone(focus.window.node)

    def test_focusing_app(self):
        """
        Ensure that focus.app() works
        """
        focus.app.node = None
        focus.app('gtk3-demo')
        self.assertEqual(focus.app.node, self.app)

    def test_focusing_app_via_application(self):
        """
        Ensure that focus.application() works
        """
        focus.app.node = None
        focus.application('gtk3-demo')
        self.assertEqual(focus.app.node, self.app)

    def test_focus_getting_bogus_attribute(self):
        self.assertRaises(AttributeError, getattr, focus, 'nosuchtype')

    def test_focus_setting_bogus_attribute(self):
        self.assertRaises(AttributeError, setattr, focus, 'nosuchtype', 'nothing')

    def test_focusing_roleName(self):
        """
        Ensure that focus.widget(roleName=...) works.
        """
        focus.widget(roleName='page tab')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_PAGE_TAB)

    def test_focus_menu(self):
        self.runDemo('Builder')
        focus.menu('File')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_MENU)

    def test_focus_menuItem(self):
        self.runDemo('Builder')
        click.menu('File')
        focus.menuItem('New')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_MENU_ITEM)

    def test_focus_button(self):
        self.runDemo('Builder')
        focus.button('Open')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_PUSH_BUTTON)

    def test_focus_table(self):
        self.runDemo('Builder')
        focus.table('')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_TABLE)

    def test_focus_tableCell(self):
        self.runDemo('Builder')
        focus.tableCell('')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_TABLE_CELL)

    def test_focus_text(self):
        self.runDemo('Assistant')
        focus.window('Page 1')
        focus.text('')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_TEXT)

    def test_focus_icon(self):
        self.runDemo('Clipboard')
        try:
            wnd = self.app.child('Clipboard demo', roleName='frame', retry=False, recursive=False)
        except SearchError:
            wnd = self.app.child('Clipboard', roleName='frame', retry=False, recursive=False)
        focus.window(wnd.name)
        focus.icon('Warning')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_ICON)


class TestKeyCombo(GtkDemoTest):

    def test_keyCombo(self):
        self.runDemo('Builder')
        keyCombo('<F7>')
        res = False
        try:
            res = focus.dialog('About Builder demo')
        except:
            try:
                res = focus.dialog('About GtkBuilder demo')
            except:
                pass
        self.assertTrue(res)

    def test_keyCombo_on_widget(self):
        self.runDemo('Builder')
        focus.button('Copy')
        keyCombo('<F7>')
        try:
            res = focus.dialog('About Builder demo')
        except:
            try:
                res = focus.dialog('About GtkBuilder demo')
            except:
                pass
        self.assertTrue(res)


class TestActions(GtkDemoTest):

    def test_click(self):
        click('Source')
        self.assertTrue(focus.widget.isSelected)

    def test_click_on_invisible_element(self):
        with self.assertRaises(ValueError):
            click("Spinner")

    def test_click_with_raw(self):
        click('Source', raw=True)
        self.assertTrue(focus.widget.isSelected)

    def test_select(self):
        select('Source')
        self.assertTrue(focus.widget.isSelected)

    def test_deselect(self):
        type('Icon View')
        click('Icon View')
        type('+')
        sleep(0.5)
        self.runDemo('Icon View Basics')
        try:
            wnd = self.app.child('GtkIconView demo', roleName='frame', recursive=False, retry=False)
        except SearchError:
            wnd = self.app.child('Icon View Basics', roleName='frame', recursive=False, retry=False)
        focus.window(wnd.name)

        focus.widget(roleName='icon')
        select()
        deselect()
        self.assertFalse(focus.widget.isSelected)

    def test_typing_on_widget(self):
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            focus.window('Dialogs')
        except SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            focus.window('Dialogs and Message Boxes')
        focus.widget(roleName='text')
        type("hello world")
        from time import sleep
        sleep(0.1)
        self.assertEqual(focus.widget.node.text, 'hello world')

    def test_custom_actions(self):
        activate("Combo Boxes")
        self.assertEqual(focus.widget.node.text, 'Combo Boxes')

    def test_blink_on_actions(self):
        config.blinkOnActions = True
        activate("Combo Boxes")
        self.assertEqual(focus.widget.node.text, 'Combo Boxes')

    def test_custom_actions_button(self):
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            focus.window('Dialogs')
        except SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            focus.window('Dialogs and Message Boxes')
        click.button('Interactive Dialog')
        self.assertTrue(focus.dialog("Interactive Dialog"))

    def test_custom_actions_menu(self):
        self.runDemo('Builder')
        try:
            wnd = self.app.child('GtkBuilder demo', roleName='frame', recursive=False, retry=False)
        except SearchError:
            wnd = self.app.child('Builder', roleName='frame', recursive=False, retry=False)
        focus.window(wnd.name)
        click.menu('File')
        click.menuItem('New')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_MENU_ITEM)

    def test_custom_actions_text(self):
        self.runDemo('Builder')
        try:
            wnd = self.app.child('GtkBuilder demo', roleName='frame', recursive=False, retry=False)
        except SearchError:
            wnd = self.app.child('Builder', roleName='frame', recursive=False, retry=False)
        focus.window(wnd.name)
        click.text('')
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_TEXT)

    def test_custom_actions_table_cell(self):
        activate.tableCell("Combo Boxes")
        self.assertTrue(isinstance(focus.widget.node, tree.Node))
        self.assertEqual(focus.widget.node.role, pyatspi.ROLE_TABLE_CELL)

    def test_throws_action_not_supported(self):
        self.runDemo('Builder')
        try:
            wnd = self.app.child('GtkBuilder demo', roleName='frame', recursive=False, retry=False)
        except SearchError:
            wnd = self.app.child('Builder', roleName='frame', recursive=False, retry=False)
        focus.window(wnd.name)
        with self.assertRaises(ActionNotSupported) as cm:
            activate.text('')
        self.assertEqual(str(cm.exception), "Cannot do 'activate' action on [text | ]")

    def test_action_on_insensitive(self):
        self.runDemo("Assistant")
        wnd = self.app.child("Page 1", roleName='frame')
        child = wnd.child("Next")
        config.ensureSensitivity = True
        with self.assertRaises(NotSensitiveError):
            output1 = trap_stdout(child.actions['click'].do())
        config.ensureSensitivity = False
        output2 = trap_stdout(child.actions['click'].do)
        #self.assertEqual(output2.strip("\n"), "")
        self.assertNotEqual(output2.strip("\n"), "") # we want the log
