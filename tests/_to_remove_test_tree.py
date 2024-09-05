#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import dogtail.config
import dogtail.predicate
import dogtail.tree
import dogtail.rawinput

from tests._to_remove_gtkdemotest import GtkDemoTest


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

    # TODO do we really need to do user data here?

    # 'debugName' (string)
    #def test_get_debugName(self):
    #    self.assertEqual(self.app.debugName, "'gtk3-demo' application")
    #    self.assertEqual(dogtail.tree.root.debugName, 'root')

    #def test_set_debugName(self):
    #    self.app.debugName = "my application"
    #    self.assertEqual(self.app.debugName, 'my application')
    #    dogtail.tree.root.debugName = "my root"
    #    self.assertEqual(dogtail.tree.root.debugName, 'my root')

    # TODO combo value never worked for me.
    #  combovalue (string):
#    def test_get_combo_value(self):
#        self.runDemo('Combo Boxes')
#        try:
#            wnd = self.app.child('Combo boxes', roleName='frame', retry=False)
#        except dogtail.tree.SearchError:
#            wnd = self.app.child('Combo Boxes', roleName='frame', retry=False)
#        combo = wnd.child(roleName='combo box')
#        self.assertEqual(combo.combovalue, 'dialog-warning')
#
#    def test_get_URI_not_implemented(self):
#        with self.assertRaises(NotImplementedError):
#            self.app.URI

    # TODO revisit, should we even bother when gtk4 does not allow text anymore?
#    def test_caretOffset(self):
#        """
#        Make sure the caret offset works as expected
#        """
#        try:
#            self.runDemo('Dialog and Message Boxes', retry=False)
#            wnd = self.app.child('Dialogs', roleName='frame', retry=False)
#        except dogtail.tree.SearchError:
#            self.runDemo('Dialogs and Message Boxes', retry=False)
#            wnd = self.app.child('Dialogs and Message Boxes', roleName='frame', retry=False)
#        entry1 = wnd.child(label='Entry 1')
#        entry2 = wnd.child(roleName='text')
#
#        # Try reading the entries:
#        self.assertEqual(entry1.text, '')
#        self.assertEqual(entry2.text, '')
#
#        # Set them...
#        s1 = "I just need a sentence"
#        s2 = "And maybe a second one to be sure"
#        entry1.text = s1
#        entry2.text = s2
#
#        # Make sure the caret offset is zero
#        self.assertEqual(entry1.caretOffset, 0)
#        self.assertEqual(entry2.caretOffset, 0)
#
#        # Set the caret offset to something ridiculous
#        entry1.caretOffset = len(s1 * 3)
#        entry2.caretOffset = len(s2 * 3)
#
#        # Make sure the caret offset only goes as far as the end of the string
#        self.assertEqual(entry1.caretOffset, len(s1))
#        self.assertEqual(entry2.caretOffset, len(s2))
#
#        def splitByOffsets(node, string):
#            # Verify the equality of node.text and string, word by word.
#            # I realize this doesn't really test dogtail itself, but that could
#            #   change in the future and I don't want to throw the code away.
#            textIface = node.queryText()
#            endOffset = -1  # We only set this now so the loop looks nicer
#            startOffset = 0
#            while startOffset != len(string):
#                (text, startOffset, endOffset) = textIface.getTextAtOffset(
#                    startOffset, pyatspi.TEXT_BOUNDARY_WORD_START)
#                self.assertEqual(startOffset, string.find(text, startOffset, endOffset))
#                startOffset = endOffset
#
#        splitByOffsets(entry1, s1)
#        splitByOffsets(entry2, s2)

    # TODO never worked for me
#    # 'combovalue' (read/write string):
#    def test_comboValue(self):
#        self.runDemo('Combo Boxes')
#        try:
#            wnd = self.app.child('Combo boxes', roleName='frame', retry=False)
#        except dogtail.tree.SearchError:
#            wnd = self.app.child('Combo Boxes', roleName='frame', retry=False)
#        combo1 = wnd.child('Items with icons').child(roleName='combo box')
#        combo1.combovalue = 'Clear'
#        self.assertEqual(combo1.combovalue, 'edit-clear')

#    def test_checked(self):
#        self.runDemo("Application Class")
#        wnd = dogtail.tree.root.application('gtk3-demo-application')
#        # TODO revisit, do we need Node. menu, menu_item, button etc? -lets do it
#        wnd.menu("Preferences").select()
#        from time import sleep
#        sleep(3)
#        checkbox = wnd.menu("Preferences").menuItem("Bold")
#        status = checkbox.checked
#        checkbox.click()
#        self.assertEqual(checkbox.checked, not status)
#        self.assertEqual(checkbox.isChecked, not status)

#    def test_dead(self):
#        self.assertFalse(self.app.dead)
#        import os
#        import signal
#        os.kill(self.pid, signal.SIGKILL)
#        dogtail.utils.doDelay(5)
#        self.assertTrue(self.app.dead)
#
#    def test_dead_empty(self):
#        node = dogtail.tree.Node()
#        self.assertTrue(node.dead)


# TODO revisit? this is not that useful to us is it?
#    def test_contains(self):
#        child = self.app.children[0]
#        position = child.position
#        self.assertTrue(child.contains(position[0]+1, position[1]+1))
# TODO revisit? this is not that useful to us is it?
#    def test_childAtPoint(self):
#        top = self.app.children[0]
#        bottom = top.children[1].children[1]
#        position = bottom.position
#        actual_acc = top.getChildAtPoint(position[0], position[1])
#        self.assertEqual(actual_acc, bottom)

# TODO Does not work on wrong coordinates in gtk3-demo
#    def test_point(self):
#        self.runDemo('Application Class')
#        wnd = dogtail.tree.root.application('gtk3-demo-application')
#        wnd.menu("Help").click() # workaround for wayland, first app focus
#        wnd.menu("Preferences").point()
#        color = wnd.menu("Preferences").menu("Color")
#        red = wnd.menu("Preferences").menu("Color").menuItem("Red")
#        self.assertFalse(red.showing)
#        color.point()
#        self.assertTrue(red.showing)
# TODO re-add this, could be useful
    # TODO revisit,type text should not be on Node, its a rawinput.
#    def test_typeText_nonfucable(self):
#        """
#        Node.typeText on non-focusable node which is not input-friendly should end in an error
#        """
#        with self.assertRaises(NotImplementedError):
#            self.app.typeText('Something')

    # TODO revisit, why ?
#    def test_getUserVisibleStrings(self):
#        child = self.app.child("Builder")
#        self.assertEqual(child.getUserVisibleStrings(), ['Builder'])
#
#    def test_satisfies(self):
#        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
#        builder = self.app.child("Builder")
#        self.assertTrue(builder.satisfies(pred))
#
#    def test_absoluteSearchPath(self):
#        self.assertEqual(
#            str(self.app.getAbsoluteSearchPath()),
#            "{/('gtk3-demo' application,False)}")
#        builder = self.app.child("Builder")
#        self.assertEqual(
#            str(builder.getAbsoluteSearchPath()),
#            "{/('gtk3-demo' application,False)/('Application Class' window,False)/(child with name='Builder' "
#            "roleName='table cell',True)}")

#    def test_compare_equal_search_paths(self):
#        builder = self.app.child("Builder")
#        builder_sp = builder.getAbsoluteSearchPath()
#        self.assertTrue(builder_sp == builder_sp)
#
#    def test_compare_unequal_search_paths_different_length(self):
#        builder = self.app.child("Builder")
#        builder_sp = builder.getAbsoluteSearchPath()
#        app_sp = self.app.getAbsoluteSearchPath()
#        self.assertFalse(builder_sp == app_sp)
#
#    def test_compare_unequal_search_paths_same_length(self):
#        builder = self.app.child("Builder")
#        assistant = self.app.child("Assistant")
#        builder_sp = builder.getAbsoluteSearchPath()
#        assistant_sp = assistant.getAbsoluteSearchPath()
#        self.assertFalse(builder_sp == assistant_sp)
#
#    def test_get_search_path_length(self):
#        builder = self.app.child("Builder")
#        builder_sp = builder.getAbsoluteSearchPath()
#        self.assertEqual(builder_sp.length(), 3)
#
#    def test_iterate_search_path(self):
#        builder = self.app.child("Builder")
#        builder_sp = builder.getAbsoluteSearchPath()
#        self.assertEqual(
#            [x[0].makeScriptVariableName() for x in builder_sp],
#            ['gtk3DemoApp', 'applicationClassWin', 'builderNode'])
#
#    def test_make_script_method_call_from_search_path(self):
#        builder = self.app.child("Builder")
#        builder_sp = builder.getAbsoluteSearchPath()
#        self.assertEqual(
#            builder_sp.makeScriptMethodCall(),
#            ".application('gtk3-demo').window('Application Class').child( name='Builder' roleName='table cell')")
#
#    def test_get_relative_search_path_for_path(self):
#        builder = self.app.child("Builder")
#        builder_sp = builder.getAbsoluteSearchPath()
#        frame_sp = self.app.window("Application Class").getAbsoluteSearchPath()
#        # FIXME: Should be "child( name="Widget (double click for demo)" roleName=\'page tab\').child( name="Builder""
#        #                  " roleName=\'table cell\')"
#        self.assertIsNone(builder_sp.getRelativePath(frame_sp))
#
#    def test_get_prefix_for_search_path(self):
#        builder = self.app.child("Builder")
#        builder_sp = builder.getAbsoluteSearchPath()
#        self.assertEqual(
#            str(builder_sp.getPrefix(1)),
#            "{/('gtk3-demo' application,False)}")

# TODO try to see what it does.

# TODO pointless search path
#    def test_get_predicate(self):
#        builder = self.app.child("Builder")
#        builder_sp = builder.getAbsoluteSearchPath()
#        pred = builder_sp.getPredicate(0)
#        self.assertEqual(type(pred), dogtail.predicate.IsAnApplicationNamed)
#        self.assertEqual(str(pred.appName), "'gtk3-demo'")

# TODO revisit, I do not see a point for relative search.
#    def test_getRelativeSearch_app(self):
#        relpath = self.app.getRelativeSearch()
#        self.assertEqual(str(relpath[0]), '[desktop frame | main]')
#        self.assertEqual(relpath[1].name.untranslatedString, 'gtk3-demo')
#        self.assertFalse(relpath[2])
#
#    def test_getRelativeSearch_widget(self):
#        builder = self.app.child("Builder")
#        relpath = builder.getRelativeSearch()
#        self.assertEqual(str(relpath[0]), '[frame | Application Class]')
#        self.assertEqual(relpath[1].describeSearchResult(), "child with name='Builder' roleName='table cell'")
#        self.assertTrue(relpath[2])

# TODO re-add recursive
    # TODO revisit, recursive was removed I never used it and I do not see the point.
#    def test_findChildren_non_recursive(self):
#        dogtail.rawinput.keyCombo("<End>")
#        self.app.child(roleName='tree table').child("Tree View").click()
#        self.app.child(roleName='tree table').child("Tree View").typeText("+")
#        self.runDemo('Tree Store')
#        try:
#            wnd = self.app.child('Card planning sheet', roleName='frame', retry=False, recursive=False)
#        except dogtail.tree.SearchError:
#            wnd = self.app.child('Tree Store', roleName='frame', retry=False, recursive=False)
#        table = wnd.child(roleName='tree table')
#        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
#        dogtail.config.config.childrenLimit = 10000
#        cells = table.findChildren(pred, recursive=False)
#        direct_cells = [cell for cell in table.children if cell.roleName == 'table cell']
#        self.assertEqual(len(cells), len(direct_cells))
