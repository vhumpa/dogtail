#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import dogtail.config
import dogtail.predicate
import dogtail.tree
import dogtail.rawinput
import pyatspi
import time
import unittest
import os

from gtkdemotest import GtkDemoTest, trap_stdout


"""
Unit tests for the dogtail.Node class

Notes on pyunit (the "unittest" module):

Test classes are written as subclass of unittest.TestCase.
A test is a method of such a class, beginning with the string "test"

unittest.main() will run all such methods.  Use "-v" to get feedback on which tests are being run.
Tests are run in alphabetical order; all failure reports are gathered at the end.

setUp and tearDown are "magic" methods, called before and after each such
test method is run.
"""
__author__ = "Dave Malcolm <dmalcolm@redhat.com>"

dogtail.config.config.logDebugToFile = False


class TestNode(GtkDemoTest):

    """
    Unit tests for the the various synthesized attributes of a Node
    """

    def test_get_bogus(self):
        """
        Getting a non-existant attribute should raise an attribute error
        """
        self.assertRaises(AttributeError, getattr, self.app, "thisIsNotAnAttribute")

    # FIXME: should setattr for a non-existant attr be allowed?

    # 'name' (read-only string):
    def test_get_name(self):
        """
        Node.name of the gtk-demo app should be "gtk-demo"
        """
        print(self.app.name)
        self.assertEqual(self.app.name, 'gtk3-demo')

        self.assertEqual(dogtail.tree.root.name, 'main')

    def test_set_name(self):
        """
        Node.name should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "name", "hello world")

    # 'debugName' (string)
    def test_get_debugName(self):
        self.assertEqual(self.app.debugName, "'gtk3-demo' application")
        self.assertEqual(dogtail.tree.root.debugName, 'root')

    def test_set_debugName(self):
        self.app.debugName = "my application"
        self.assertEqual(self.app.debugName, 'my application')
        dogtail.tree.root.debugName = "my root"
        self.assertEqual(dogtail.tree.root.debugName, 'my root')

    # 'roleName' (read-only string):
    def test_get_roleName(self):
        """
        roleName of the gtk3-demo app should be "application"
        """
        self.assertEqual(self.app.roleName, 'application')

    def test_set_roleName(self):
        """
        Node.roleName should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "roleName", "hello world")

    # 'role' (read-only atspi role enum):
    def test_get_role(self):
        """
        Node.role for a gtk-demo app should be SPI_ROLE_APPLICATION
        """
        self.assertEqual(self.app.role, dogtail.tree.pyatspi.ROLE_APPLICATION)

    def test_set_role(self):
        """
        Node.role should be read-only
        """
        # FIXME should be AttributeError?
        self.assertRaises(RuntimeError, self.app.__setattr__, "role", pyatspi.Atspi.Role(1))

    # 'description' (read-only string):
    def test_get_description(self):
        # FIXME: can we get a more interesting test case here?
        self.assertEqual(self.app.description, "")

    def test_set_description(self):
        """
        Node.description should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "description", "hello world")

    # 'parent' (read-only Node instance):
    def test_get_parent(self):
        # the app has a parent if gnome-shell is used, so parent.parent is a
        # safe choice
        if [x for x in self.app.applications() if x.name == 'gnome-shell']:
            self.assertEqual(self.app.parent.parent, None)
        self.assertEqual(self.app.children[0].parent, self.app)

    def test_set_parent(self):
        """
        Node.parent should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "parent", None)

    # 'children' (read-only list of Node instances):
    def test_get_children(self):
        """
        A fresh gtk-demo app should have a single child: the window.
        """
        kids = self.app.children
        self.assertEqual(len(kids), 1)
        self.assertEqual(kids[0].name, "Application Class")
        self.assertEqual(kids[0].roleName, "frame")

    def test_set_children(self):
        """
        Node.children should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "children", [])

    def test_get_children_with_limit(self):
        haveWarnedAboutChildrenLimit = False
        dogtail.config.config.childrenLimit = 1
        widget = self.app.child(roleName='tree table')
        self.assertEqual(len(widget.children), 1)

    #  combovalue (string):
    def test_get_combo_value(self):
        self.runDemo('Combo Boxes')
        try:
            wnd = self.app.child('Combo boxes', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            wnd = self.app.child('Combo Boxes', roleName='frame', retry=False)
        combo = wnd.child(roleName='combo box')
        self.assertEqual(combo.combovalue, 'dialog-warning')

    def test_get_URI_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.app.URI

    # 'text' (string):
    def test_set_text(self):
        """
        Use gtk-demo's text entry example to check that reading and writing
        Node.text works as expected
        """
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs and Message Boxes', roleName='frame', retry=False)
        wnd.button('Interactive Dialog').click()
        dlg = self.app.dialog('Interactive Dialog')
        entry1 = dlg.child(label='Entry 1')
        entry2 = dlg.child(roleName='text')

        # Try reading the entries:
        self.assertEqual(entry1.text, "")
        self.assertEqual(entry2.text, "")

        # Set them...
        entry1.text = "hello"
        entry2.text = "world"

        # Ensure that they got set:
        self.assertEqual(entry1.text, "hello")
        self.assertEqual(entry2.text, "world")

        # and try again, searching for them again, to ensure it actually
        # affected the UI:
        self.assertEqual(dlg.child(label='Entry 1').text, "hello")
        self.assertEqual(dlg.child(label='Entry 2').text, "world")

        # Ensure app.text is None
        self.assertEqual(self.app.text, None)

        # Ensure a label's text is read-only as expected:
        # FIXME: this doesn't work; the label has no 'text'; it has a name.  we wan't a readonly text entry
        # label = dlg.child('Entry 1')
        # self.assertRaises(dogtail.tree.ReadOnlyError, label.text.__setattr__, "text", "hello world")

        # FIXME: should we assert that things are logged and delays are added?
        # FIXME: should have a test case involving the complex GtkTextView
        # widget

    def test_text_set_error(self):
        with self.assertRaises(AttributeError):
            self.app.text = 'something'

    def test_caretOffset(self):
        """
        Make sure the caret offset works as expected
        """
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs and Message Boxes', roleName='frame', retry=False)
        entry1 = wnd.child(label='Entry 1')
        entry2 = wnd.child(roleName='text')

        # Try reading the entries:
        self.assertEqual(entry1.text, '')
        self.assertEqual(entry2.text, '')

        # Set them...
        s1 = "I just need a sentence"
        s2 = "And maybe a second one to be sure"
        entry1.text = s1
        entry2.text = s2

        # Make sure the caret offset is zero
        self.assertEqual(entry1.caretOffset, 0)
        self.assertEqual(entry2.caretOffset, 0)

        # Set the caret offset to something ridiculous
        entry1.caretOffset = len(s1 * 3)
        entry2.caretOffset = len(s2 * 3)

        # Make sure the caret offset only goes as far as the end of the string
        self.assertEqual(entry1.caretOffset, len(s1))
        self.assertEqual(entry2.caretOffset, len(s2))

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
                self.assertEqual(startOffset, string.find(text, startOffset, endOffset))
                startOffset = endOffset

        splitByOffsets(entry1, s1)
        splitByOffsets(entry2, s2)

    # 'combovalue' (read/write string):
    def test_comboValue(self):
        self.runDemo('Combo Boxes')
        try:
            wnd = self.app.child('Combo boxes', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            wnd = self.app.child('Combo Boxes', roleName='frame', retry=False)
        combo1 = wnd.child('Items with icons').child(roleName='combo box')
        combo1.combovalue = 'Clear'
        self.assertEqual(combo1.combovalue, 'edit-clear')

    # 'stateSet' (read-only StateSet instance):
    def test_getStateSet(self):
        """
        Node.sensitive should be False for the gtk-demo app node
        """
        self.assertFalse(self.app.sensitive)

    def test_setStateSet(self):
        """
        Node.stateSet should be read-only
        """
        # FIXME should be AttributeError?
        self.assertRaises(RuntimeError, self.app.__setattr__, "states", pyatspi.StateSet())

    # 'relations' (read-only list of atspi.Relation instances):
    def test_get_relations(self):
        # FIXME once relations are used for something other than labels
        pass

    # 'labelee' (read-only list of Node instances):
    def test_get_labelee(self):
        """
        Entry1/2's labelee should be a text widget
        """
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs and Message Boxes', roleName='frame', retry=False)
        label = wnd.child(roleName='label', name='Entry 1')
        self.assertEqual(label.labelee.roleName, 'text')
        self.assertEqual(label.labellee.roleName, 'text')

    def test_set_labelee(self):
        """
        Node.labelee should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "labellee", None)

    def test_get_labeler(self):
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs and Message Boxes', roleName='frame', retry=False)
        text = wnd.findChildren(dogtail.predicate.GenericPredicate(roleName='text'))[1]
        self.assertEqual(text.labeler.name, 'Entry 1')
        self.assertEqual(text.labeller.name, 'Entry 1')

    def test_set_labeller(self):
        """
        Node.labeller should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "labeller", None)

    # 'sensitive' (read-only boolean):
    def test_get_sensitive(self):
        """
        Node.sensitive should not be set for the gtk-demo app.
        It should be set for the window within the app.
        """
        self.assertFalse(self.app.sensitive)
        self.assertTrue(self.app.children[0].sensitive)

    def test_set_sensitive(self):
        """
        Node.sensitive should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "sensitive", True)

    # 'showing' (read-only boolean):
    def test_get_showing(self):
        """
        Node.showing should not be set for the gtk-demo.  It should be set for the window within the app
        """
        self.assertFalse(self.app.showing)
        self.assertTrue(self.app.children[0].showing)

    def test_set_showing(self):
        """
        Node.showing should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "showing", True)

    # 'visible' (read-only boolean):
    def test_get_visible(self):
        """
        Node.visible reflects a node property if is should be render or not
        """
        self.assertTrue(self.app.child(roleName='frame').visible)
        self.assertFalse(self.app.child(roleName='table column header').visible)

    def test_set_visible(self):
        """
        Node.visible should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "visible", False)

    # 'actions' (read-only list of Action instances):
    def test_get_actions(self):
        """
        Node.actions should be an empty list for the app node
        """
        self.assertEqual(len(self.app.actions), 0)

    def test_set_actions(self):
        """
        Node.actions should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "actions", {})

    # 'extents' (readonly tuple):
    def test_get_extents(self):
        """
        Node.extents should be a 4-tuple for a window, with non-zero size
        """
        (x, y, w, h) = self.app.children[0].extents
        self.assertTrue(w > 0)
        self.assertTrue(h > 0)

    def test_get_extens_wrong(self):
        """
        Some accessible do not specify size nor position
        """
        self.assertIsNone(self.app.extents)

    def test_set_extents(self):
        """
        Node.extents should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "extents", (0, 0, 640, 480))

    # 'position' (readonly tuple):
    def test_get_position(self):
        """
        Node.position should be a 2-tuple for a window
        """
        (x, y) = self.app.children[0].position
        self.assertTrue(isinstance(x, int))
        self.assertTrue(isinstance(y, int))

    def test_get_position_not_implemented(self):
        """
        Some accessible do not specify position (nor size)
        """
        with self.assertRaises(NotImplementedError):
            self.app.position

    def test_set_position(self):
        """
        Node.position should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "position", (0, 0))

    # 'size' (readonly tuple):
    def test_get_size(self):
        """
        Node.size should be a 2-tuple for a window, with non-zero values
        """
        (w, h) = self.app.children[0].size
        self.assertTrue(w > 0)
        self.assertTrue(h > 0)

    def test_get_size_not_implemented(self):
        """
        Some accessible do not specify size (nor position)
        """
        with self.assertRaises(NotImplementedError):
            self.app.size

    def test_set_size(self):
        """
        Node.size should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "size", (640, 480))

    # 'toolkitName' (readonly string):
    def test_get_toolkit(self):
        """
        Node.toolkitName is a read-only string
        """
        self.assertEqual(self.app.toolkitName, "gtk")

    def test_set_toolkit(self):
        """
        Node.toolkit should be read-only
        """
        self.assertRaises(AttributeError, self.app.__setattr__, "toolkitName", "gtk")

    # 'ID'
    def test_get_ID(self):
        """
        Node.id should be numeric
        """
        self.assertEqual(type(self.app.id), type(42))

    def test_set_ID(self):
        """
        Node.id should be read-only
        """
        self.assertRaises(AttributeError, setattr, self.app, "id", 42)

    def test_checked(self):
        self.runDemo("Application Class")
        wnd = dogtail.tree.root.application('gtk3-demo-application')
        wnd.menu("Preferences").select()
        from time import sleep
        sleep(3)
        checkbox = wnd.menu("Preferences").menuItem("Bold")
        status = checkbox.checked
        checkbox.click()
        self.assertEqual(checkbox.checked, not status)
        self.assertEqual(checkbox.isChecked, not status)

    def test_dead(self):
        self.assertFalse(self.app.dead)
        import os
        import signal
        os.kill(self.pid, signal.SIGKILL)
        dogtail.utils.doDelay(5)
        self.assertTrue(self.app.dead)

    def test_dead_empty(self):
        node = dogtail.tree.Node()
        self.assertTrue(node.dead)

    # https://bugzilla.gnome.org/show_bug.cgi?id=710730
    # GError: Method "Contains" with signature "iin" on interface "org.a11y.atspi.Component" doesn't exist
    def test_contains(self):
        child = self.app.children[0]
        position = child.position
        self.assertTrue(child.contains(position[0]+1, position[1]+1))

    def test_childAtPoint(self):
        top = self.app.children[0]
        bottom = top.children[1].children[1]
        position = bottom.position
        actual_acc = top.getChildAtPoint(position[0], position[1])
        self.assertEqual(actual_acc, bottom)

    def test_click(self):
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs and Message Boxes', roleName='frame', retry=False)
        wnd.button('Interactive Dialog').click()
        self.assertTrue(self.app.dialog("Interactive Dialog").showing)

    def test_doubleClick(self):
        builder = self.app.child("Builder")
        self.assertEqual(len([x for x in self.app.children if x.name in ['GtkBuilder demo', 'Builder']]), 0)
        builder.doubleClick()
        self.assertEqual(len([x for x in self.app.children if x.name in ['GtkBuilder demo', 'Builder']]), 2)

    def test_point(self):
        self.runDemo('Application Class')
        wnd = dogtail.tree.root.application('gtk3-demo-application')
        wnd.menu("Help").click() # workaround for wayland, first app focus
        wnd.menu("Preferences").point()
        color = wnd.menu("Preferences").menu("Color")
        red = wnd.menu("Preferences").menu("Color").menuItem("Red")
        self.assertFalse(red.showing)
        color.point()
        self.assertTrue(red.showing)

    def test_typeText_nonfucable(self):
        """
        Node.typeText on non-focusable node which is not input-friendly should end in an error
        """
        with self.assertRaises(NotImplementedError):
            self.app.typeText('Something')


class TestSelection(GtkDemoTest):

    def test_tabs(self):
        """
        Tabs in the gtk-demo should be selectable, and be queryable for
        "isSelected", and the results should change as they are selected.
        """
        # Use the Info/Source tabs of gtk-demo:
        info = self.app.child('Info')
        source = self.app.child('Source')

        # Check initial state:
        self.assertTrue(info.isSelected)
        self.assertFalse(source.isSelected)

        # Select other tab:
        source.select()

        # Check new state:
        self.assertFalse(info.isSelected)
        self.assertTrue(source.isSelected)

    def test_iconView(self):
        self.app.child(roleName='tree table').typeText("Icon View")
        self.app.child(roleName='tree table').child("Icon View").click()
        self.app.child(roleName='tree table').child("Icon View").typeText("+")
        self.runDemo('Icon View Basics')
        try:
            wnd = self.app.child('GtkIconView demo', roleName='frame', recursive=False, retry=False)
        except dogtail.tree.SearchError:
            wnd = self.app.child('Icon View Basics', roleName='frame', recursive=False, retry=False)

        pane = wnd.child(roleName="layered pane")
        icons = pane.children

        pane.selectAll()
        self.assertNotIn(False, [x.selected for x in icons])
        pane.select_all()
        self.assertNotIn(False, [x.selected for x in icons])
        pane.select_child(0)
        self.assertTrue(icons[0].selected)
        self.assertNotIn(False, [x.selected for x in icons])


class TestValue(GtkDemoTest):

    def test_get_value(self):
        """
        The scrollbar starts out at position zero.
        """
        sb = self.app.child(roleName='scroll bar')
        self.assertEqual(sb.value, 0)

    def test_set_value(self):
        """
        Ensure that we can set the value of the scrollbar.
        """
        sb = self.app.findChildren(dogtail.predicate.GenericPredicate(roleName='scroll bar'))[1]
        sb.value = 100
        self.assertEqual(sb.value, 100)

    def test_min_value(self):
        """
        Ensure that the minimum value for the scrollbar is correct.
        """
        sb = self.app.findChildren(dogtail.predicate.GenericPredicate(roleName='scroll bar'))[1]
        self.assertEqual(sb.minValue, 0)

    def test_max_value(self):
        sb = self.app.findChildren(dogtail.predicate.GenericPredicate(roleName='scroll bar'))[1]
        self.assertTrue(sb.maxValue > 250)

    def test_min_value_increment(self):
        """
        Ensure that the minimum value increment of the scrollbar is an int.
        """
        sb = self.app.findChildren(dogtail.predicate.GenericPredicate(roleName='scroll bar'))[1]
        self.assertEqual(sb.minValueIncrement, sb.minValueIncrement)


class TestSearching(GtkDemoTest):

    def test_findChildren(self):
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
        self.assertEqual(len(tableCells), counter)

    def test_findChild_lambda(self):
        """
        Ensure that the lambda usage works as expected with Node.findChild
        """
        try:
            self.app.findChild(lambda x: x.roleName == 'page tab list')
        except dogtail.tree.SearchError:
            self.fail("Got a SearchError trying to find the page tab list")

    def test_findChildren2(self):
        """
        Ensure that there are two tabs in the second page tab list.
        """
        pred = dogtail.predicate.GenericPredicate(roleName='page tab list')
        pageTabList = self.app.findChildren(pred)
        pred = dogtail.predicate.GenericPredicate(roleName='page tab')
        # only one page tab list present since gtk3-demo 3.14
        pageTabs = pageTabList[0].findChildren(pred)
        self.assertEqual(len(pageTabs), 5)

    def test_findChildren2_lambda(self):
        """
        Ensure that there ic correct number of tabs in the first page tab list, use lambdas
        """
        pageTabList = self.app.findChildren(lambda x: x.roleName == 'page tab list')
        pageTabs = pageTabList[0].findChildren(lambda x: x.roleName == 'page tab')
        self.assertEqual(len(pageTabs), 5)

    def test_findChildren_lambdas(self):
        """
        Ensure that the lambda usage works as expected in Node.findChildren
        """
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs and Message Boxes', roleName='frame', retry=False)
        texts = wnd.findChildren(lambda x: x.roleName == 'text', isLambda=True)
        self.assertEqual(len(texts), 2)
        self.assertEqual(texts[0].roleName, 'text')
        self.assertEqual(texts[1].roleName, 'text')
        texts1 = wnd.findChildren(lambda x: x.roleName == 'text' and x.labeler.name == 'Entry 1', isLambda=True)
        self.assertEqual(len(texts1), 1)
        self.assertEqual(texts1[0].roleName, 'text')
        self.assertEqual(texts1[0].labeler.name, 'Entry 1')
        texts2 = wnd.findChildren(lambda x: x.roleName == 'text' and x.showing, isLambda=True)
        self.assertEqual(len(texts2), 2)
        self.assertEqual(texts2[0].roleName, 'text')
        self.assertTrue(texts2[0].showing)
        self.assertEqual(texts2[1].roleName, 'text')
        self.assertTrue(texts2[1].showing)

    def test_findAncestor(self):
        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
        child = self.app.child("Builder")
        parent = child.findAncestor(pred)
        self.assertIn(child, parent.children)
        pred = dogtail.predicate.GenericPredicate(roleName='frame')
        parent = child.findAncestor(pred)
        self.assertIn(parent, self.app.children)
        # No ancestor found
        self.assertIsNone(parent.findAncestor(pred))

    def test_isChild(self):
        parent = self.app.child(roleName='tree table')
        self.assertTrue(parent.isChild("Builder"))

    def test_getUserVisibleStrings(self):
        child = self.app.child("Builder")
        self.assertEqual(child.getUserVisibleStrings(), ['Builder'])

    def test_satisfies(self):
        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
        builder = self.app.child("Builder")
        self.assertTrue(builder.satisfies(pred))

    def test_absoluteSearchPath(self):
        self.assertEqual(
            str(self.app.getAbsoluteSearchPath()),
            "{/('gtk3-demo' application,False)}")
        builder = self.app.child("Builder")
        self.assertEqual(
            str(builder.getAbsoluteSearchPath()),
            "{/('gtk3-demo' application,False)/('Application Class' window,False)/(child with name='Builder' "
            "roleName='table cell',True)}")

    def test_compare_equal_search_paths(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertTrue(builder_sp == builder_sp)

    def test_compare_unequal_search_paths_different_length(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        app_sp = self.app.getAbsoluteSearchPath()
        self.assertFalse(builder_sp == app_sp)

    def test_compare_unequal_search_paths_same_length(self):
        builder = self.app.child("Builder")
        assistant = self.app.child("Assistant")
        builder_sp = builder.getAbsoluteSearchPath()
        assistant_sp = assistant.getAbsoluteSearchPath()
        self.assertFalse(builder_sp == assistant_sp)

    def test_get_search_path_length(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertEqual(builder_sp.length(), 3)

    def test_iterate_search_path(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertEqual(
            [x[0].makeScriptVariableName() for x in builder_sp],
            ['gtk3DemoApp', 'applicationClassWin', 'builderNode'])

    def test_make_script_method_call_from_search_path(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertEqual(
            builder_sp.makeScriptMethodCall(),
            ".application('gtk3-demo').window('Application Class').child( name='Builder' roleName='table cell')")

    def test_get_relative_search_path_for_path(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        frame_sp = self.app.window("Application Class").getAbsoluteSearchPath()
        # FIXME: Should be "child( name="Widget (double click for demo)" roleName=\'page tab\').child( name="Builder""
        #                  " roleName=\'table cell\')"
        self.assertIsNone(builder_sp.getRelativePath(frame_sp))

    def test_get_prefix_for_search_path(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertEqual(
            str(builder_sp.getPrefix(1)),
            "{/('gtk3-demo' application,False)}")

    def test_get_predicate(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        pred = builder_sp.getPredicate(0)
        self.assertEqual(type(pred), dogtail.predicate.IsAnApplicationNamed)
        self.assertEqual(str(pred.appName), "'gtk3-demo'")

    def test_getRelativeSearch_app(self):
        relpath = self.app.getRelativeSearch()
        self.assertEqual(str(relpath[0]), '[desktop frame | main]')
        self.assertEqual(relpath[1].name.untranslatedString, 'gtk3-demo')
        self.assertFalse(relpath[2])

    def test_getRelativeSearch_widget(self):
        builder = self.app.child("Builder")
        relpath = builder.getRelativeSearch()
        self.assertEqual(str(relpath[0]), '[frame | Application Class]')
        self.assertEqual(relpath[1].describeSearchResult(), "child with name='Builder' roleName='table cell'")
        self.assertTrue(relpath[2])

    def test_findChildren_non_recursive(self):
        dogtail.rawinput.keyCombo("<End>")
        self.app.child(roleName='tree table').child("Tree View").click()
        self.app.child(roleName='tree table').child("Tree View").typeText("+")
        self.runDemo('Tree Store')
        try:
            wnd = self.app.child('Card planning sheet', roleName='frame', retry=False, recursive=False)
        except dogtail.tree.SearchError:
            wnd = self.app.child('Tree Store', roleName='frame', retry=False, recursive=False)
        table = wnd.child(roleName='tree table')
        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
        dogtail.config.config.childrenLimit = 10000
        cells = table.findChildren(pred, recursive=False)
        direct_cells = [cell for cell in table.children if cell.roleName == 'table cell']
        self.assertEqual(len(cells), len(direct_cells))

    def test_find_by_shortcut(self):
        self.runDemo('Builder')
        try:
            wnd = self.app.child('GtkBuilder demo', roleName='frame', recursive=False, retry=False)
        except dogtail.tree.SearchError:
            wnd = self.app.child('Builder', roleName='frame', recursive=False, retry=False)

        self.assertIsNotNone(wnd.menu("File"))
        self.assertIsNotNone(wnd.menu("File").menuItem("New"))
        self.assertIsNotNone(wnd.button("Save"))
        self.assertIsNotNone(wnd.childNamed("File"))
        self.assertIsNotNone(self.app.tab("Info"))

    def test_find_by_shortcut2(self):
        try:
            self.runDemo('Dialog and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs', roleName='frame', retry=False)
        except dogtail.tree.SearchError:
            self.runDemo('Dialogs and Message Boxes', retry=False)
            wnd = self.app.child('Dialogs and Message Boxes', roleName='frame', retry=False)
        self.assertIsNotNone(wnd.childLabelled("Entry 1"))
        self.assertIsNotNone(wnd.button("Message Dialog"))


# A painful point of collision between strings in python2 and python3!
@unittest.skipIf(os.system('ls /usr/bin/gedit') != 0, "Skipping, need gedit")
class TestUnicodeNames(unittest.TestCase):
    def setUp(self):
        import dogtail.config
        dogtail.config.config.logDebugToStdOut = True
        dogtail.config.config.logDebugToFile = True
        dogtail.config.config.logDebugToStdOut = True
        dogtail.config.config.debugSearching = False
        dogtail.config.config.searchCutoffCount = 3
        import dogtail.utils
        self.pid = dogtail.utils.run('gedit')
        self.ver = os.popen('gedit -V').read().split()[-1]
        try:
            self.app = dogtail.tree.root.application('org.gnome.gedit')
        except Exception:
            self.app = dogtail.tree.root.application('gedit')

    def test_unicode_char_in_name(self):
        self.app.child('Menu', roleName='toggle button').click()
        unicode_button = None
        unicode_button = self.app.child(name=u'Find and Replace…', roleName='push button')
        assert unicode_button is not None

    def test_unicode_char_in_name_click(self):
        self.app.child('Menu', roleName='toggle button').click()
        unicode_button = self.app.child(name=u'Find and Replace…', roleName='push button')
        unicode_button.click()
        dialog = None
        t_ver = tuple(map(int, (self.ver.split("."))))
        chooser_name = u'Open' if t_ver < (40, 0) else u"Open Files"
        try:
            dialog = self.app.child(name=chooser_name, roleName='file chooser')
        except dogtail.tree.SearchError:
            self.fail()
        assert dialog is not None

    def test_unicode_logging_nocrash(self):
        try:
            self.app.child(name='…Other stuff…', roleName='push button')
            self.fail()
        except dogtail.tree.SearchError:
            pass

    def tearDown(self):
        import signal
        os.kill(self.pid, signal.SIGKILL)
        os.system('killall gedit > /dev/null 2>&1')
        # Sleep just enough to let the app actually die.
        # AT-SPI doesn't like being hammered too fast.
        time.sleep(0.5)

class TestDump(GtkDemoTest):

    def test_dump_to_stdout(self):
        child = self.app.child('Source')
        output = trap_stdout(child.dump)
        self.assertEqual(
            output,
            """[page tab | Source]
 [scroll pane | ]
  [text | ]
  [scroll bar | ]
  [scroll bar | ]""")

    def test_dump_with_actions(self):
        child = self.app.child('Builder', roleName='table cell')
        output = trap_stdout(child.dump)
        self.assertEqual(
            output,
            """[table cell | Builder]
 [action | activate |  ]
 [action | edit |  ]
 [action | expand or contract |  ]""")
