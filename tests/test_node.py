#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for the dogtail.Node class

Notes on pyunit (the "unittest" module):

Test classes are written as subclass of unittest.TestCase.
A test is a method of such a class, beginning with the string "test"

unittest.main() will run all such methods.  Use "-v" to get feedback on which tests are being run.  Tests are run in alphabetical order; all failure reports are gathered at the end.

setUp and tearDown are "magic" methods, called before and after each such
test method is run.
"""
__author__ = "Dave Malcolm <dmalcolm@redhat.com>"

import unittest
import dogtail.tree
import dogtail.predicate
import dogtail.config
dogtail.config.config.logDebugToFile = False
import pyatspi
from nose.tools import nottest
from gtkdemotest import GtkDemoTest, trap_stdout


class TestNodeAttributes(GtkDemoTest):

    """
    Unit tests for the the various synthesized attributes of a Node
    """

    def testGetBogus(self):
        "Getting a non-existant attribute should raise an attribute error"
        self.assertRaises(
            AttributeError, getattr, self.app, "thisIsNotAnAttribute")

    # FIXME: should setattr for a non-existant attr be allowed?

    # 'name' (read-only string):
    def testGetName(self):
        """
        Node.name of the gtk-demo app should be "gtk-demo"
        """
        self.assertEquals(self.app.name, 'gtk3-demo')

        self.assertEquals(dogtail.tree.root.name, 'main')

    def testSetName(self):
        "Node.name should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "name", "hello world")

    # 'roleName' (read-only string):
    def testGetRoleName(self):
        """
        roleName of the gtk-demo app should be "application"
        """
        self.assertEquals(self.app.roleName, 'application')

    def testSetRoleName(self):
        """Node.roleName should be read-only"""
        self.assertRaises(
            AttributeError, self.app.__setattr__, "roleName", "hello world")

    # 'role' (read-only atspi role enum):
    def testGetRole(self):
        """Node.role for a gtk-demo app should be SPI_ROLE_APPLICATION"""
        self.assertEquals(self.app.role, dogtail.tree.pyatspi.ROLE_APPLICATION)

    def testSetRole(self):
        """Node.role should be read-only"""
        # FIXME should be AttributeError?
        self.assertRaises(
            RuntimeError, self.app.__setattr__, "role", pyatspi.Atspi.Role(1))

    # 'description' (read-only string):
    def testGetDescription(self):
        # FIXME: can we get a more interesting test case here?
        self.assertEquals(self.app.description, "")

    def testSetDescription(self):
        "Node.description should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "description", "hello world")

    # 'parent' (read-only Node instance):
    def testGetParent(self):
        # the app has a parent if gnome-shell is used, so parent.parent is a
        # safe choice
        if filter(lambda x: x.name == 'gnome-shell', self.app.applications()):
            self.assertEquals(self.app.parent.parent, None)
        self.assertEquals(self.app.children[0].parent, self.app)

    def testSetParent(self):
        "Node.parent should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "parent", None)

    # 'children' (read-only list of Node instances):
    def testGetChildren(self):
        "A fresh gtk-demo app should have a single child: the window."
        kids = self.app.children
        self.assertEquals(len(kids), 1)
        self.assertEquals(kids[0].name, "GTK+ Code Demos")
        self.assertEquals(kids[0].roleName, "frame")

    def testSetChildren(self):
        "Node.children should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "children", [])

    # 'text' (string):
    @nottest
    def testSimpleTextEntry(self):
        """
        Use gtk-demo's text entry example to check that reading and writing
        Node.text works as expected
        """
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        wnd.button('Interactive Dialog').click()
        dlg = self.app.dialog('Interactive Dialog')
        entry1 = dlg.child(label='Entry 1')
        entry2 = dlg.child(label='Entry 2')

        # Try reading the entries:
        self.assertEquals(entry1.text, "")
        self.assertEquals(entry2.text, "")

        # Set them...
        entry1.text = "hello"
        entry2.text = "world"

        # Ensure that they got set:
        self.assertEquals(entry1.text, "hello")
        self.assertEquals(entry2.text, "world")

        # and try again, searching for them again, to ensure it actually
        # affected the UI:
        self.assertEquals(dlg.child(label='Entry 1').text, "hello")
        self.assertEquals(dlg.child(label='Entry 2').text, "world")

        # Ensure app.text is None
        self.assertEquals(self.app.text, None)

        # Ensure a label's text is read-only as expected:
        # FIXME: this doesn't work; the label has no 'text'; it has a name.  we wan't a readonly text entry
        # label = dlg.child('Entry 1')
        # self.assertRaises(dogtail.tree.ReadOnlyError, label.text.__setattr__, "text", "hello world")

        # FIXME: should we assert that things are logged and delays are added?
        # FIXME: should have a test case involving the complex GtkTextView
        # widget

    @nottest
    def testCaretOffset(self):
        "Make sure the caret offset works as expected"
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        entry1 = wnd.child(label='Entry 1')
        entry2 = wnd.child(label='Entry 2')

        # Try reading the entries:
        self.assertEquals(entry1.text, '')
        self.assertEquals(entry2.text, '')

        # Set them...
        s1 = "I just need a sentence"
        s2 = "And maybe a second one to be sure"
        entry1.text = s1
        entry2.text = s2

        # Make sure the caret offset is zero
        self.assertEquals(entry1.caretOffset, 0)
        self.assertEquals(entry2.caretOffset, 0)

        # Set the caret offset to something ridiculous
        entry1.caretOffset = len(s1 * 3)
        entry2.caretOffset = len(s2 * 3)

        # Make sure the caret offset only goes as far as the end of the string
        self.assertEquals(entry1.caretOffset, len(s1))
        self.assertEquals(entry2.caretOffset, len(s2))

        def splitByOffsets(node, string):
            # Verify the equality of node.text and string, word by word.
            # I realize this doesn't really test dogtail itself, but that could
            #   change in the future and I don't want to throw the code away.
            textIface = node.queryText()
            endOffset = -1  # We only set this now so the loop looks nicer
            startOffset = 0
            while startOffset != len(string):
                (text, startOffset, endOffset) = textIface.getTextAtOffset(
                    startOffset, pyatspi.TEXT_BOUNDARY_WORD_START)
                self.assertEquals(startOffset,
                                  string.find(text, startOffset, endOffset))
                startOffset = endOffset

        splitByOffsets(entry1, s1)
        splitByOffsets(entry2, s2)

    # 'combovalue' (read/write string):
    @nottest
    def testSetComboValue(self):
        self.runDemo('Combo boxes')
        wnd = self.app.window('Combo boxes')
        combo1 = wnd.child('Some stock icons').child(roleName='combo box')
        combo1.combovalue = 'Clear'
        self.assertEquals(combo1.combovalue, 'Clear')

    # 'stateSet' (read-only StateSet instance):
    def testGetStateSet(self):
        "Node.sensitive should be False for the gtk-demo app node"
        self.assert_(not self.app.sensitive)

    def testSetStateSet(self):
        "Node.stateSet should be read-only"
        # FIXME should be AttributeError?
        self.assertRaises(
            RuntimeError, self.app.__setattr__, "states", pyatspi.StateSet())

    # 'relations' (read-only list of atspi.Relation instances):
    def testGetRelations(self):
        # FIXME once relations are used for something other than labels
        pass

    # 'labelee' (read-only list of Node instances):
    @nottest
    def testGetLabelee(self):
        "Entry1/2's labelee should be a text widget"
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        label = wnd.child(roleName='label')
        self.assertEquals(label.labelee.roleName, 'text')

    def testSetLabelee(self):
        "Node.labelee should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "labellee", None)

    # 'labeler' (read-only list of Node instances):
    # def testGetLabeler(self):
    #    "The text areas in the 'Dialogs' window should have labelers."
    #    self.runDemo('Dialog and Message Boxes')
    #    wnd = self.app.window('Dialogs')
    #    text = wnd.child(roleName = 'text')
    #    self.assertEquals(text.labeler.name, 'Entry 2')

    def testSetLabeller(self):
        "Node.labeller should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "labeller", None)

    # 'sensitive' (read-only boolean):
    def testGetSensitive(self):
        """
        Node.sensitive should not be set for the gtk-demo app.
        It should be set for the window within the app.
        """
        self.assert_(not self.app.sensitive)
        self.assert_(self.app.children[0].sensitive)

    def testSetSensitive(self):
        "Node.sensitive should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "sensitive", True)

    # 'showing' (read-only boolean):
    def testGetShowing(self):
        "Node.showing should not be set for the gtk-demo.  It should be set for the window within the app"
        self.assert_(not self.app.showing)
        self.assert_(self.app.children[0].showing)

    def testSetShowing(self):
        "Node.showing should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "showing", True)

    # 'actions' (read-only list of Action instances):
    def testGetActions(self):
        "Node.actions should be an empty list for the app node"
        self.assertEquals(len(self.app.actions), 0)

    def testSetActions(self):
        "Node.actions should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__, "actions", {})

    # 'extents' (readonly tuple):
    def testGetExtents(self):
        "Node.extents should be a 4-tuple for a window, with non-zero size"
        (x, y, w, h) = self.app.children[0].extents
        self.assert_(w > 0)
        self.assert_(h > 0)

    def testSetExtents(self):
        "Node.extents should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "extents", (0, 0, 640, 480))

    # 'position' (readonly tuple):
    def testGetPosition(self):
        "Node.position should be a 2-tuple for a window"
        (x, y) = self.app.children[0].position

    def testSetPosition(self):
        "Node.position should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "position", (0, 0))

    # 'size' (readonly tuple):
    def testGetSize(self):
        "Node.size should be a 2-tuple for a window, with non-zero values"
        (w, h) = self.app.children[0].size
        self.assert_(w > 0)
        self.assert_(h > 0)

    def testSetSize(self):
        "Node.size should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "size", (640, 480))

    # 'toolkitName' (readonly string):
    def testGetToolkit(self):
        self.assertEquals(self.app.toolkitName, "gtk")

    def testSetToolkit(self):
        "Node.toolkit should be read-only"
        self.assertRaises(
            AttributeError, self.app.__setattr__, "toolkitName", "gtk")

    # 'ID'
    def testGetID(self):
        "Node.id should be numeric"
        self.assertEquals(type(self.app.id), type(42))

    def testSetID(self):
        "Node.id should be read-only"
        self.assertRaises(AttributeError, setattr, self.app, "id", 42)


class TestSelection(GtkDemoTest):

    def testTabs(self):
        """
        Tabs in the gtk-demo should be selectable, and be queryable for
        "isSelected", and the results should change as they are selected.
        """
        # Use the Info/Source tabs of gtk-demo:
        info = self.app.child('Info')
        source = self.app.child('Source')

        # Check initial state:
        self.assert_(info.isSelected)
        self.assert_(not source.isSelected)

        # Select other tab:
        source.select()

        # Check new state:
        self.assert_(not info.isSelected, False)
        self.assert_(source.isSelected)

        # Deselect tab:
        # source.deselect()

        # Check state:
        # self.assert_(info.isSelected)
        #self.assert_(not source.isSelected)


class TestValue(GtkDemoTest):

    def testGetValue(self):
        "The scrollbar starts out at position zero."
        sb = self.app.child(roleName='scroll bar')
        self.assertEquals(sb.value, 0)

#    def testSetValue(self):
#        "Ensure that we can set the value of the scrollbar."
#        sb = self.app.child(roleName = 'scroll bar')
#        sb.value = 100
#        self.assertEquals(sb.value, 100)

    def testMinValue(self):
        "Ensure that the minimum value for the scrollbar is correct."
        sb = self.app.child(roleName='scroll bar')
        self.assertEquals(sb.minValue, 0)

#    def testMaxValue(self):
#        "Ensure that the maximum value for the scrollbar is plausible."
#        sb = self.app.child(roleName = 'scroll bar')
#        self.assert_(sb.maxValue > 250)

    def testMinValueIncrement(self):
        "Ensure that the minimum value increment of the scrollbar is an int."
        sb = self.app.child(roleName='scroll bar')
        self.assertEquals(sb.minValueIncrement, sb.minValueIncrement)


class TestSearching(GtkDemoTest):
    # FIXME: should test the various predicates and the search methods of Node

    def testFindChildren(self):
        """
        Ensure that there are the correct number of table cells in the list
        of demos.
        """
        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
        tableCells = self.app.findChildren(pred)

        def get_table_cells_recursively(node):
            counter = 0
            for child in node.children:
                if child.roleName == 'table cell':
                    counter += 1
                counter += get_table_cells_recursively(child)
            return counter

        counter = get_table_cells_recursively(self.app)
        self.assertEquals(len(tableCells), counter)

    def testFindChildren2(self):
        "Ensure that there are two tabs in the second page tab list."
        pred = dogtail.predicate.GenericPredicate(roleName='page tab list')
        pageTabLists = self.app.findChildren(pred)
        pred = dogtail.predicate.GenericPredicate(roleName='page tab')
        # The second page tab list is the one with the 'Info' and 'Source' tabs
        pageTabs = pageTabLists[1].findChildren(pred)
        self.assertEquals(len(pageTabs), 6)

    def testFindChildrenLambdas(self):
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        texts = wnd.findChildren(lambda x: x.roleName=='text', isLambda = True)
        self.assertEquals(len(texts), 2)
        self.assertEquals(texts[0].roleName, 'text')
        self.assertEquals(texts[1].roleName, 'text')
        texts1 = wnd.findChildren(lambda x: x.roleName=='text' and x.labeler.name == 'Entry 1', isLambda = True)
        self.assertEquals(len(texts1), 1)
        self.assertEquals(texts1[0].roleName, 'text')
        self.assertEquals(texts1[0].labeler.name, 'Entry 1')
        texts2 = wnd.findChildren(lambda x: x.roleName=='text' and x.showing, isLambda = True)
        self.assertEquals(len(texts2), 2)
        self.assertEquals(texts2[0].roleName, 'text')
        self.assertTrue(texts2[0].showing)
        self.assertEquals(texts2[1].roleName, 'text')
        self.assertTrue(texts2[1].showing)

    # def testFindChildrenNonRecursive(self):
    #     """
    #     Ensure that there are the correct number of table cells in the Tree
    #     Store demo.
    #     """
    # The next several lines exist to expand the 'Tree View' item and
    # scroll down, so that runDemo() will work.
    # FIXME: make runDemo() handle this for us.
    #     treeViewCell = self.app.child('Tree View', roleName = 'table cell')
    #     treeViewCell.typeText('+')
    #     dogtail.tree.doDelay()
    #     sb = self.app.child(roleName = 'scroll bar')
    #     sb.value = sb.maxValue
    #     self.runDemo('Tree Store')
    #     wnd = self.app.window('Card planning sheet')
    #     table = wnd.child(roleName = 'tree table')
    #     pred = dogtail.predicate.GenericPredicate(roleName = 'table cell')
    #     dogtail.config.config.childrenLimit = 10000
    #     cells = table.findChildren(pred, recursive = False)
    #     direct_cells = filter(lambda cell: cell.roleName=='table cell', table.children)
    #     self.assertEquals(len(cells), len(direct_cells))


class TestActions(GtkDemoTest):
    # FIXME: should test the various actions
    pass


class TestProcedural(GtkDemoTest):
    # FIXME: should test the procedural API
    pass


class TestExceptions(GtkDemoTest):

    @nottest
    def test_exception(self):
        # Kill the gtk-demo prematurely:
        import os
        import signal
        os.kill(self.pid, signal.SIGKILL)

        from gi.repository import GLib
        # Ensure that we get an exception when we try to work further with it:
        self.assertRaises(GLib.GError, self.app.dump)


class TestConfiguration(unittest.TestCase):

    def test_get_set_all_properties(self):
        for option in dogtail.config.config.defaults.keys():
            print("Setting config.%s property" % option)
            value = ''
            if 'Dir' in option:
                value = '/tmp/dogtail/'  # Special value for dir-related properties
            dogtail.config.config.__setattr__(option, value)
            self.assertEquals(dogtail.config.config.__getattr__(option), value)

    def test_default_directories_created(self):
        import os.path
        self.assertEquals(
            os.path.isdir(dogtail.config.config.scratchDir), True)
        self.assertEquals(os.path.isdir(dogtail.config.config.logDir), True)
        self.assertEquals(os.path.isdir(dogtail.config.config.dataDir), True)

    def test_set(self):
        self.assertRaises(
            AttributeError, setattr, dogtail.config.config, 'nosuchoption', 42)

    def test_get(self):
        self.assertRaises(
            AttributeError, getattr, dogtail.config.config, 'nosuchoption')

    def helper_create_directory_and_set_option(self, path, property_name):
        import os.path
        if os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        dogtail.config.config.__setattr__(property_name, path)
        self.assertEquals(os.path.isdir(path), True)

    def test_create_scratch_directory(self):
        new_folder = "/tmp/dt"
        self.helper_create_directory_and_set_option(new_folder, 'scratchDir')

    def test_create_data_directory(self):
        new_folder = "/tmp/dt_data"
        self.helper_create_directory_and_set_option(new_folder, 'dataDir')

    def test_create_log_directory(self):
        new_folder = "/tmp/dt_log"
        self.helper_create_directory_and_set_option(new_folder, 'logDir')

    def test_load(self):
        dogtail.config.config.load({'actionDelay': 2.0})
        self.assertEquals(dogtail.config.config.actionDelay, 2.0)

    def test_reset(self):
        default_actionDelay = dogtail.config.config.defaults['actionDelay']
        dogtail.config.config.actionDelay = 2.0
        dogtail.config.config.reset()
        self.assertEquals(
            dogtail.config.config.actionDelay, default_actionDelay)


class TestDump(GtkDemoTest):

    @nottest
    def test_dump_to_stdout(self):
        child = self.app.child('Source')
        output = trap_stdout(child.dump)
        self.assertEquals(
            output,
            """[page tab | Source]
             [scroll pane | ]
              [text | ]
              [scroll bar | ]
               [action | activate |  ]
              [scroll bar | ]
               [action | activate |  ]""")
