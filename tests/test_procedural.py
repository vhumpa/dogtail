#!/usr/bin/python
"""
Unit tests for the dogtail.procedural API
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

from dogtail.procedural import focus, keyCombo, deselect, select, click, tree, FocusError, run, config, type
config.logDebugToFile = False
config.logDebugToStdOut = True
import pyatspi
from gtkdemotest import GtkDemoTest, trap_stdout
from nose.tools import nottest


class GtkDemoTest(GtkDemoTest):

    def setUp(self):
        self.pid = run('gtk3-demo')
        self.app = focus.application.node

    # FIXME: Implement doubleclick() in d.procedural and override the other
    # methods of Node.GtkDemoTest


class TestFocusApplication(GtkDemoTest):

    def testFocusingBogusNameWithoutAFatalError(self):
        config.fatalErrors = False
        output = trap_stdout(focus.application, "should not be found")
        self.assertTrue(
            'The requested widget could not be focused: "should not be found" application' in output)

    def testThrowExceptionOnFocusingBogusName(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.application, "should not be found")

    def testFocusingBasic(self):
        "Ensure that focus.application() sets focus.application.node properly"
        focus.application.node = None
        focus.application("gtk3-demo")
        self.assertEquals(focus.application.node, self.app)


class TestFocusWindow(GtkDemoTest):

    def testFocusingBogusNameWithoutAFatalError(self):
        config.fatalErrors = False
        output = trap_stdout(focus.window, "should not be found")
        self.assertEquals(focus.window.node, None)
        self.assertTrue(
            'The requested widget could not be focused: "should not be found" window' in output)

    def testThrowExceptionOnFocusingBogusName(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.window, "should not be found")


class TestFocusDialog(GtkDemoTest):

    def testFocusingBogusNameWithoutAFatalError(self):
        config.fatalErrors = False
        output = trap_stdout(focus.dialog, "should not be found")
        self.assertEquals(focus.dialog.node, None)
        self.assertTrue(
            'The requested widget could not be focused: "should not be found" dialog' in output)

    def testThrowExceptionOnFocusingBogusName(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.dialog, "should not be found")


class TestFocusWidget(GtkDemoTest):

    def testFocusingEmptyName(self):
        self.assertRaises(TypeError, focus.widget)

    def testFocusingBogusNameWithoutAFatalError(self):
        config.fatalErrors = False
        output = trap_stdout(focus.widget, "should not be found")
        self.assertEquals(focus.widget.node, None)
        self.assertTrue(
            'The requested widget could not be focused: child with name="should not be found"' in output)

    def testThrowExceptionOnFocusingBogusName(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.widget, "should not be found")

    def testFocusingBasic(self):
        "Ensure that focus.widget('foo') finds a node with name 'foo'"
        focus.widget("Application window")
        self.assertEquals(focus.widget.name, "Application window")


class TestFocus(GtkDemoTest):

    def testInitialState(self):
        "Ensure that focus.widget, focus.dialog and focus.window are None " + \
            "initially."
        self.assertEquals(focus.widget.node, None)
        self.assertEquals(focus.dialog.node, None)
        self.assertEquals(focus.window.node, None)

    def testFocusingApp(self):
        "Ensure that focus.app() works"
        focus.app.node = None
        focus.app('gtk3-demo')
        self.assertEquals(focus.app.node, self.app)

    def testFocusingAppViaApplication(self):
        "Ensure that focus.application() works"
        focus.app.node = None
        focus.application('gtk3-demo')
        self.assertEquals(focus.app.node, self.app)

    def testFocusGettingBogusAttribute(self):
        self.assertRaises(AttributeError, getattr, focus, 'nosuchtype')

    def testFocusSettingBogusAttribute(self):
        self.assertRaises(
            AttributeError, setattr, focus, 'nosuchtype', 'nothing')

    def testFocusingRoleName(self):
        "Ensure that focus.widget(roleName=...) works."
        focus.widget(roleName='page tab')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_PAGE_TAB)

    def testFocusMenu(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        focus.menu('File')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_MENU)

    def testFocusMenuItem(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        click.menu('File')
        focus.menuItem('New')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_MENU_ITEM)

    def testFocusButton(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        focus.button('Open')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_PUSH_BUTTON)

    def testFocusTable(self):
        self.runDemo('Builder')
        focus.window('GtkBuilder demo')
        focus.table('')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TABLE)

    def testFocusTableCell(self):
        self.runDemo('Builder')
        focus.window('GtkBuilder demo')
        focus.tableCell('')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TABLE_CELL)

    def testFocusText(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        focus.text('')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TEXT)


class TestKeyCombo(GtkDemoTest):

    def testKeyCombo(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        keyCombo("<ctrl>a")
        focus.dialog('About GTK+ Code Demos')


class TestActions(GtkDemoTest):

    def testClick(self):
        click('Source')
        self.assertTrue(focus.widget.isSelected)

    def testClickWithRaw(self):
        click('Source', raw=True)
        self.assertTrue(focus.widget.isSelected)

    def testSelect(self):
        select('Source')
        self.assertTrue(focus.widget.isSelected)

    @nottest
    def testDeselect(self):
        type('Icon View')
        click('Icon View')
        type('+')
        self.runDemo('Icon View Basics')
        focus.window('GtkIconView demo')

        focus.widget(roleName='icon')
        select()
        deselect()
        self.assertFalse(focus.widget.isSelected)

    def testTyping(self):
        self.runDemo('Dialog and Message Boxes')
        focus.window('Dialogs')
        focus.widget(roleName='text')
        type("hello world")
        self.assertEquals(focus.widget.node.text, 'hello world')
