#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import dogtail.predicate
import dogtail.tree
import unittest

"""
Unit tests for the dogtail.predicate package
"""


class TestPredicate(unittest.TestCase):

    class DummyNode:

        def __init__(self, name='', roleName='', description=''):
            self.name = name
            self.roleName = roleName
            self.description = description
            self.labeller = None

    def test_capitalization(self):
        self.assertEqual(dogtail.predicate.makeCamel("gnome-terminal"), "gnomeTerminal")
        self.assertEqual(dogtail.predicate.makeCamel("Evolution - Mail"), "evolutionMail")
        self.assertEqual(
            dogtail.predicate.makeCamel('self.assertEquals(makeCamel("Evolution - Mail"), "evolutionMail")'),
            "selfAssertequalsMakecamelEvolutionMailEvolutionmail")

    def test_abstract_class(self):
        predicate = dogtail.predicate.Predicate()
        self.assertRaises(NotImplementedError, predicate.satisfiedByNode, None)
        self.assertRaises(NotImplementedError, predicate.makeScriptMethodCall, None)
        self.assertRaises(NotImplementedError, predicate.makeScriptVariableName)
        self.assertRaises(NotImplementedError, predicate.describeSearchResult, None)

    def test_correct_equality(self):
        predicate1 = dogtail.predicate.Predicate()
        predicate2 = dogtail.predicate.Predicate()
        self.assertEqual(predicate1, predicate2)

    def test_incorrect_equality(self):
        predicate = dogtail.predicate.Predicate()
        self.assertNotEqual(predicate, self)

    def test_predicates_application(self):
        dummyApp = self.DummyNode("dummy", 'application')
        appPredicate = dogtail.predicate.IsAnApplicationNamed(dummyApp.name)
        self.assertTrue(appPredicate.satisfiedByNode(dummyApp))
        self.assertEqual(appPredicate.makeScriptMethodCall(True), "application('dummy')")
        self.assertEqual(appPredicate.makeScriptVariableName(), 'dummyApp')

    def test_predicates_window(self):
        dummyWin = self.DummyNode("dummy", 'frame')
        self.assertTrue(dogtail.predicate.IsAWindow().satisfiedByNode(dummyWin))
        self.assertEqual(dogtail.predicate.IsAWindow().describeSearchResult(), 'window')

    def test_predicates_window_named(self):
        dummyWin = self.DummyNode("dummy", 'frame')
        frameNamedPredicate = dogtail.predicate.IsAWindowNamed(dummyWin.name)
        self.assertTrue(frameNamedPredicate.satisfiedByNode(dummyWin))
        self.assertEqual(frameNamedPredicate.makeScriptMethodCall(False), "window('dummy')")
        self.assertEqual(frameNamedPredicate.makeScriptVariableName(), 'dummyWin')

    def test_predicates_menu_named(self):
        dummyMenu = self.DummyNode("dummy", 'menu')
        menuNamedPredicate = dogtail.predicate.IsAMenuNamed(dummyMenu.name)
        self.assertTrue(menuNamedPredicate.satisfiedByNode(dummyMenu))
        self.assertEqual(menuNamedPredicate.makeScriptMethodCall(False), "menu('dummy', recursive=False)")
        self.assertEqual(menuNamedPredicate.makeScriptVariableName(), 'dummyMenu')

    def test_predicates_menu_item_named(self):
        dummyMenuItem = self.DummyNode("dummy", 'menu item')
        menuItemNamedPredicate = dogtail.predicate.IsAMenuItemNamed(dummyMenuItem.name)
        self.assertTrue(menuItemNamedPredicate.satisfiedByNode(dummyMenuItem))
        self.assertEqual(menuItemNamedPredicate.makeScriptMethodCall(False), "menuItem('dummy', recursive=False)")
        self.assertEqual(menuItemNamedPredicate.makeScriptVariableName(), 'dummyMenuItem')

    def test_predicates_text_entry_named(self):
        dummyText = self.DummyNode("dummy", 'text')
        textNamedPredicate = dogtail.predicate.IsATextEntryNamed(dummyText.name)
        self.assertTrue(textNamedPredicate.satisfiedByNode(dummyText))
        self.assertEqual(textNamedPredicate.makeScriptMethodCall(False), "textentry('dummy', recursive=False)")
        self.assertEqual(textNamedPredicate.makeScriptVariableName(), 'dummyEntry')

    def test_predicates_button_named(self):
        dummyButton = self.DummyNode("dummy", 'push button')
        buttonNamedPredicate = dogtail.predicate.IsAButtonNamed(dummyButton.name)
        self.assertTrue(buttonNamedPredicate.satisfiedByNode(dummyButton))
        self.assertEqual(buttonNamedPredicate.makeScriptMethodCall(False), "button('dummy', recursive=False)")
        self.assertEqual(buttonNamedPredicate.makeScriptVariableName(), 'dummyButton')

    def test_predicates_page_tab_named(self):
        dummyTab = self.DummyNode("dummy", 'page tab')
        pageTabNamedPredicate = dogtail.predicate.IsATabNamed(dummyTab.name)
        self.assertTrue(pageTabNamedPredicate.satisfiedByNode(dummyTab))
        self.assertEqual(pageTabNamedPredicate.makeScriptMethodCall(False), "tab('dummy', recursive=False)")
        self.assertEqual(pageTabNamedPredicate.makeScriptVariableName(), 'dummyTab')

    def test_predicates_generic_by_name(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        genericPredicateByName = dogtail.predicate.GenericPredicate(name=dn1.name)
        self.assertTrue(genericPredicateByName.satisfiedByNode(dn1))
        self.assertEqual(genericPredicateByName.makeScriptMethodCall(
            False), "child( name='dummy name 1', recursive=False)")
        self.assertEqual(genericPredicateByName.makeScriptVariableName(), 'dummyName1Node')

    def test_predicates_generic_by_roleName(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        genericPredicateByRole = dogtail.predicate.GenericPredicate(roleName=dn1.roleName)
        self.assertTrue(genericPredicateByRole.satisfiedByNode(dn1))
        self.assertEqual(genericPredicateByRole.makeScriptMethodCall(
            False), "child( roleName='dummy role 1', recursive=False)")
        self.assertEqual(genericPredicateByRole.makeScriptVariableName(), 'dummyRole1Node')

    def test_predicates_generic_by_description(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        genericPredicateByDescription = dogtail.predicate.GenericPredicate(description=dn1.description)
        self.assertTrue(genericPredicateByDescription.satisfiedByNode(dn1))
        self.assertEqual(genericPredicateByDescription.makeScriptMethodCall(
            False), "child( description='dummy desc 1', recursive=False)")
        self.assertEqual(genericPredicateByDescription.makeScriptVariableName(), 'dummyDesc1Node')

    def test_predicates_generic_by_label(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        dn2 = self.DummyNode('dummy name 2', 'dummy role 2', 'dummy desc 2')
        dn2.labeller = dn1
        genericPredicateByLabel = dogtail.predicate.GenericPredicate(label=dn1.name)
        self.assertTrue(genericPredicateByLabel.satisfiedByNode(dn2))
        self.assertEqual(genericPredicateByLabel.makeScriptMethodCall(
            False), "child(label='dummy name 1', recursive=False)")
        self.assertEqual(genericPredicateByLabel.makeScriptVariableName(), 'dummyName1Node')

    def test_predicates_named(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        genericNamedPredicate = dogtail.predicate.IsNamed(dn1.name)
        self.assertTrue(genericNamedPredicate.satisfiedByNode(dn1))
        self.assertEqual(genericNamedPredicate.makeScriptMethodCall(
            False), "child(name='dummy name 1', recursive=False)")
        self.assertEqual(genericNamedPredicate.makeScriptVariableName(), 'dummyName1Node')

    def test_predicates_labelled_as(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        dn2 = self.DummyNode('dummy name 2', 'dummy role 2', 'dummy desc 2')
        dn2.labeller = dn1
        genericLabelledPredicate = dogtail.predicate.IsLabelledAs(dn1.name)
        self.assertTrue(genericLabelledPredicate.satisfiedByNode(dn2))
        self.assertFalse(genericLabelledPredicate.satisfiedByNode(dn1))
        self.assertEqual(genericLabelledPredicate.makeScriptMethodCall(
            False), "child(label='dummy name 1', recursive=False)")
        self.assertEqual(genericLabelledPredicate.makeScriptVariableName(), 'dummyName1Node')

    def test_predicates_dialog_named(self):
        dn1 = self.DummyNode('dummy name 1', 'dialog', 'dummy desc 1')
        genericNamedPredicate = dogtail.predicate.IsADialogNamed(dn1.name)
        self.assertTrue(genericNamedPredicate.satisfiedByNode(dn1))
        self.assertEqual(genericNamedPredicate.makeScriptMethodCall(False), "dialog('dummy name 1')")
        self.assertEqual(genericNamedPredicate.makeScriptVariableName(), 'dummyName1Dlg')
