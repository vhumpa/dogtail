#!/usr/bin/env python
"""
Unit tests for the dogtail.Node class

Notes on pyunit (the "unittest" module):

Test classes are written as subclass of unittest.TestCase.
A test is a method of such a class, beginning with the string "test"

unittest.main() will run all such methods.  Use "-v" to get feedback on which tests are being run.  Tests are run in alphabetical order; all failure reports are gathered at the end.

setUp and tearDown are "magic" methods, called before and after each such
test method is run.
"""
__author__="Dave Malcolm <dmalcolm@redhat.com>"

import unittest
import dogtail.tree
import atspi

class GtkDemoTest(unittest.TestCase):
    """
    TestCase subclass which handles bringing up and shutting down gtk-demo as a fixture.  Used for writing other test cases.
    """
    def setUp(self):
        import dogtail.utils
        self.pid = dogtail.utils.run('gtk-demo')
        self.app = dogtail.tree.root.application('gtk-demo')

    def tearDown(self):
        import os, signal
        os.kill(self.pid, signal.SIGKILL)

    def runDemo(self, demoName):
        """
        Click on the named demo within the gtk-demo app.
        """
        tree = self.app.child(roleName="tree table")
        tree.child(demoName).doAction('activate')

class TestNodeAttributes(GtkDemoTest):
    """
    Unit tests for the the various synthesized attributes of a Node
    """
    def testGetBogus(self):
        "Getting a non-existant attribute should raise an attribute error"
        self.assertRaises(AttributeError, self.app.__getattr__,  "thisIsNotAnAttribute")

    #FIXME: should setattr for a non-existant attr be allowed?
    
    # 'name' (read-only string):
    def testGetName(self):
        """
        Node.name of the gtk-demo app should be "gtk-demo"
        """
        self.assertEquals(self.app.name, 'gtk-demo')

        self.assertEquals(dogtail.tree.root.name, 'main')

    def testSetName(self):
        "Node.name should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "name", "hello world")
    
    # 'roleName' (read-only string):
    def testGetRoleName(self):
        """
        roleName of the gtk-demo app should be "application"
        """
        self.assertEquals(self.app.roleName, 'application')

    def testSetRoleName(self):
        "Node.roleName should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "roleName", "hello world")

    # 'role' (read-only atspi role enum):
    def testGetRole(self):
        "Node.role for a gtk-demo app should be SPI_ROLE_APPLICATION"
        self.assertEquals(self.app.role, atspi.SPI_ROLE_APPLICATION)

    def testSetRole(self):
        "Node.role should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "role", "hello world")

    # 'description' (read-only string):
    def testGetDescription(self):
        # FIXME: can we get a more interesting test case here?
        self.assertEquals(self.app.description, "")

    def testSetDescription(self):
        "Node.description should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "description", "hello world")

    # 'parent' (read-only Node instance):
    def testGetParent(self):
        # the app appears to not have a parent:
        self.assertEquals(self.app.parent, None)

        # ensure that a child of the app has the app as a parent (would be good to have proper node equality/identity...)
        self.assertEquals(self.app.children[0].parent.name, "gtk-demo")

    def testSetParent(self):
        "Node.parent should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "parent", None)

    # 'children' (read-only list of Node instances):
    def testGetChildren(self):
        "A fresh gtk-demo app should have a single child: the window."
        kids = self.app.children
        self.assertEquals(len(kids), 1)
        self.assertEquals(kids[0].name, "GTK+ Code Demos")
        self.assertEquals(kids[0].roleName, "frame")

    def testSetChildren(self):
        "Node.children should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "children", [])

    # 'text' (string):
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
        
        # and try again, searching for them again, to ensure it actually affected the UI:
        self.assertEquals(dlg.child(label='Entry 1').text, "hello")
        self.assertEquals(dlg.child(label='Entry 2').text, "world")

        # Ensure app.text is None
        self.assertEquals(self.app.text, None)

        # Ensure a label's text is read-only as expected:
        # FIXME: this doesn't work; the label has no 'text'; it has a name.  we wan't a readonly text entry
        # label = dlg.child('Entry 1')
        # self.assertRaises(dogtail.tree.ReadOnlyError, label.text.__setattr__,  "text", "hello world")

        # FIXME: should we assert that things are logged and delays are added?
        # FIXME: should have a test case involving the complex GtkTextView widget

    # FIXME: 'passwordText' (write-only string):
    # is there one of these inside gtk-demo?
    
    # FIXME: 'caretOffset' (read/write int):

    # 'combovalue' (write-only string):
    def testGetComboValue(self):
        # FIXME: should have the code raise a WriteOnly exception and check for it here
        pass

    def testSetComboValue(self):
        # FIXME: to be written
        #self.runDemo('Combo boxes')
        #wnd = self.app.window('Combo boxes')
        #combo1 = wnd.child(label="Some stock icons")
        pass

    # 'stateSet' (read-only StateSet instance):
    def testGetStateSet(self):
        "Node.stateSet should not contain SPI_STATE_SENSITIVE for the gtk-demo app node"
        val = self.app.stateSet
        self.assert_(not val.contains(atspi.SPI_STATE_SENSITIVE))

    def testSetStateSet(self):
        "Node.stateSet should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "stateSet", [])

    # 'relations' (read-only list of atspi.Relation instances):
    def testGetRelations(self):
        # FIXME
        pass

    def testSetRelations(self):
        "Node.relations should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "relations", [])

    # 'labellee' (read-only list of Node instances):
    def testGetLabellee(self):
        # FIXME
        pass

    def testSetLabellee(self):
        "Node.labellee should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "labellee", None)

    # 'labeller' (read-only list of Node instances):
    def testGetLabeller(self):
        # FIXME
        pass

    def testSetLabeller(self):
        "Node.labeller should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "labeller", None)

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
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "sensitive", True)

    # 'showing' (read-only boolean):
    def testGetShowing(self):
        "Node.showing should not be set for the gtk-demo.  It should be set for the window within the app"
        self.assert_(not self.app.showing)
        self.assert_(self.app.children[0].showing)

    def testSetShowing(self):
        "Node.showing should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "showing", True)

    # 'actions' (read-only list of Action instances):
    def testGetActions(self):
        "Node.actions should be an empty list for the app node"
        self.assertEquals(len(self.app.actions), 0) 
        # FIXME test some common widgets
   
    def testSetActions(self):
        "Node.actions should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "actions", [])

    # 'extents' (readonly tuple):
    def testGetExtents(self):
        "Node.extents should be a 4-tuple for a window, with non-zero size"
        (x,y,w,h) = self.app.children[0].extents
        self.assert_(w>0)
        self.assert_(h>0)

    def testSetExtents(self):
        "Node.extents should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "extents", (0,0,640,480))

    # 'position' (readonly tuple):
    def testGetPosition(self):
        "Node.position should be a 2-tuple for a window"
        (x,y) = self.app.children[0].position

    def testSetPosition(self):
        "Node.position should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "position", (0,0))

    # 'size' (readonly tuple):
    def testGetSize(self):
        "Node.size should be a 2-tuple for a window, with non-zero values"
        (w,h) = self.app.children[0].size
        self.assert_(w>0)
        self.assert_(h>0)

    def testSetSize(self):
        "Node.size should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "size", (640,480))

    # 'toolkit' (readonly string):
    def testGetToolkit(self):
        self.assertEquals(self.app.toolkit, "GAIL")

    def testSetToolkit(self):
        "Node.toolkit should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "toolkit", "GAIL")

    # 'version'
    def testGetVersion(self):
        import dogtail.distro
        expectedVersion = dogtail.distro.packageDb.getVersion('gail')
        self.assertEquals(self.app.version, str(expectedVersion))

    def testSetVersion(self):
        "Node.version should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "version", 42)

    # 'ID'
    def testGetID(self):
        "Node.ID should be numeric"
        self.assertEquals(type(self.app.ID), type(42))

    def testSetID(self):
        "Node.ID should be read-only"
        self.assertRaises(dogtail.tree.ReadOnlyError, self.app.__setattr__,  "ID", 42)

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
        #source.deselect()

        # Check state:
        #self.assert_(info.isSelected)
        #self.assert_(not source.isSelected)


class TestPredicates(GtkDemoTest):
    # FIXME: should test the various predicates and the search methods of Node
    pass

class TestActions(GtkDemoTest):
    # FIXME: should test the various actions
    pass

class TestProcedural(GtkDemoTest):
    # FIXME: should test the procedural API
    pass

class TestExceptions(GtkDemoTest):
    def test_exception(self):
        # Kill the gtk-demo prematurely:
        import os, signal
        os.kill(self.pid, signal.SIGKILL)

        # Ensure that we get an exception when we try to work further with it:
        self.assertRaises(atspi.SpiException, self.app.__getattr__, "name")

if __name__ == '__main__':
    unittest.main()
