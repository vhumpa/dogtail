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
    # 'name' (read-only string):
    def testGetName(self):
        self.assertEquals(self.app.name, 'gtk-demo')

        self.assertEquals(dogtail.tree.root.name, 'main')

    def testSetName(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass
    
    # 'roleName' (read-only string):
    def testGetRoleName(self):
        self.assertEquals(self.app.roleName, 'application')

    def testSetRoleName(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'role' (read-only atspi role enum):
    def testGetRole(self):
        self.assertEquals(self.app.role, atspi.SPI_ROLE_APPLICATION)

    def testSetRole(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'description' (read-only string):
    def testGetDescription(self):
        # FIXME: can we get a more interesting test case here?
        self.assertEquals(self.app.description, "")

    def testSetDescription(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'parent' (read-only Node instance):
    def testGetParent(self):
        # the app appears to not have a parent:
        self.assertEquals(self.app.parent, None)

        # ensure that a child of the app has the app as a parent (would be good to have proper node equality/identity...)
        self.assertEquals(self.app.children[0].parent.name, "gtk-demo")

    def testSetParent(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'children' (read-only list of Node instances):
    def testGetChildren(self):
        kids = self.app.children
        self.assertEquals(len(kids), 1)
        self.assertEquals(kids[0].name, "GTK+ Code Demos")
        self.assertEquals(kids[0].roleName, "frame")

    def testSetChildren(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'text' (string):
    def testSimpleTextEntry(self):
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
        # self.assertRaises(ReadOnlyError, label.text.__setattr__,  "text", "hello world")

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
        val = self.app.stateSet
        self.assert_(not val.contains(atspi.SPI_STATE_SENSITIVE))

    def testSetStateSet(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'relations' (read-only list of atspi.Relation instances):
    def testGetRelations(self):
        # FIXME
        pass

    def testSetRole(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'labellee' (read-only list of Node instances):
    def testGetRole(self):
        # FIXME
        pass

    def testSetRole(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'labeller' (read-only list of Node instances):
    def testGetRole(self):
        # FIXME
        pass

    def testSetRole(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'sensitive' (read-only boolean):
    def testGetSensitive(self):
        self.assert_(not self.app.sensitive)
        self.assert_(self.app.children[0].sensitive)

    def testSetSensitive(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'showing' (read-only boolean):
    def testGetShowing(self):
        self.assert_(not self.app.showing)
        self.assert_(self.app.children[0].showing)

    def testSetShowing(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'actions' (read-only list of Action instances):
    def testGetActions(self):
        self.assertEquals(len(self.app.actions), 0) 
        # FIXME test some common widgets
   
    def testSetActions(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'extents' (readonly tuple):
    def testGetExtents(self):
        (x,y,w,h) = self.app.children[0].extents

    def testSetExtents(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'position' (readonly tuple):
    def testGetPosition(self):
        (x,y) = self.app.children[0].position

    def testSetPosition(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'size' (readonly tuple):
    def testGetSize(self):
        (w,h) = self.app.children[0].size

    def testSetSize(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'toolkit' (readonly string):
    def testGetToolkit(self):
        self.assertEquals(self.app.toolkit, "GAIL")

    def testSetToolkit(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'version'
    def testGetVersion(self):
        import dogtail.distro
        expectedVersion = dogtail.distro.packageDb.getVersion('gail')
        self.assertEquals(self.app.version, str(expectedVersion))

    def testSetVersion(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

    # 'ID'
    def testGetID(self):
        # all we know is that it should be numeric:
        self.assertEquals(type(self.app.ID), type(42))

    def testSetID(self):
        # FIXME: should have the code raise a ReadOnly exception and check for it here
        pass

class TestSelection(GtkDemoTest):
    def testTabs(self):
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
    

if __name__ == '__main__':
    unittest.main()
