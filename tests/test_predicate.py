#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for the dogtail.predicate package
"""
import unittest
import dogtail.tree
import dogtail.predicate


class TestPredicate(unittest.TestCase):

    class DummyNode:

        def __init__(self, name='', roleName='', description=''):
            self.name = name
            self.roleName = roleName
            self.description = description
            self.labeller = None

    def test_capitalization(self):
        self.assertEquals(
            dogtail.predicate.makeCamel("gnome-terminal"), "gnomeTerminal")
        self.assertEquals(
            dogtail.predicate.makeCamel("Evolution - Mail"), "evolutionMail")
        self.assertEquals(
            dogtail.predicate.makeCamel(
                'self.assertEquals(makeCamel("Evolution - Mail"), "evolutionMail")'),
            "selfAssertequalsMakecamelEvolutionMailEvolutionmail")

    def test_abstract_class(self):
        predicate = dogtail.predicate.Predicate()
        self.assertRaises(NotImplementedError, predicate.satisfiedByNode, None)
        self.assertRaises(
            NotImplementedError, predicate.makeScriptMethodCall, None)
        self.assertRaises(
            NotImplementedError, predicate.makeScriptVariableName)
        self.assertRaises(
            NotImplementedError, predicate.describeSearchResult, None)

    def test_correct_equality(self):
        predicate1 = dogtail.predicate.Predicate()
        predicate2 = dogtail.predicate.Predicate()
        self.assertEquals(predicate1, predicate2)

    def test_incorrect_equality(self):
        predicate = dogtail.predicate.Predicate()
        self.assertNotEquals(predicate, self)

    def test_predicates_application(self):
        dummyApp = self.DummyNode('dummy', 'application')
        appPredicate = dogtail.predicate.IsAnApplicationNamed(dummyApp.name)
        self.assertTrue(appPredicate.satisfiedByNode(dummyApp))
        self.assertEquals(
            appPredicate.makeScriptMethodCall(True), u'application("dummy")')
        self.assertEquals(appPredicate.makeScriptVariableName(), u'dummyApp')

    def test_predicates_window(self):
        dummyWin = self.DummyNode('dummy', 'frame')
        self.assertTrue(
            dogtail.predicate.IsAWindow().satisfiedByNode(dummyWin))
        self.assertEquals(
            dogtail.predicate.IsAWindow().describeSearchResult(), 'window')

    def test_predicates_window_named(self):
        dummyWin = self.DummyNode('dummy', 'frame')
        frameNamedPredicate = dogtail.predicate.IsAWindowNamed(dummyWin.name)
        self.assertTrue(frameNamedPredicate.satisfiedByNode(dummyWin))
        self.assertEquals(
            frameNamedPredicate.makeScriptMethodCall(False), u'window("dummy")')
        self.assertEquals(
            frameNamedPredicate.makeScriptVariableName(), u'dummyWin')

    def test_predicates_menu_named(self):
        dummyMenu = self.DummyNode('dummy', 'menu')
        menuNamedPredicate = dogtail.predicate.IsAMenuNamed(dummyMenu.name)
        self.assertTrue(menuNamedPredicate.satisfiedByNode(dummyMenu))
        self.assertEquals(menuNamedPredicate.makeScriptMethodCall(
            False), u'menu("dummy", recursive=False)')
        self.assertEquals(
            menuNamedPredicate.makeScriptVariableName(), u'dummyMenu')

    def test_predicates_menu_item_named(self):
        dummyMenuItem = self.DummyNode('dummy', 'menu item')
        menuItemNamedPredicate = dogtail.predicate.IsAMenuItemNamed(
            dummyMenuItem.name)
        self.assertTrue(menuItemNamedPredicate.satisfiedByNode(dummyMenuItem))
        self.assertEquals(menuItemNamedPredicate.makeScriptMethodCall(
            False), u'menuItem("dummy", recursive=False)')
        self.assertEquals(
            menuItemNamedPredicate.makeScriptVariableName(), u'dummyMenuItem')

    def test_predicates_text_entry_named(self):
        dummyText = self.DummyNode('dummy', 'text')
        textNamedPredicate = dogtail.predicate.IsATextEntryNamed(
            dummyText.name)
        self.assertTrue(textNamedPredicate.satisfiedByNode(dummyText))
        self.assertEquals(textNamedPredicate.makeScriptMethodCall(
            False), u'textentry("dummy", recursive=False)')
        self.assertEquals(
            textNamedPredicate.makeScriptVariableName(), u'dummyEntry')

    def test_predicates_button_named(self):
        dummyButton = self.DummyNode('dummy', 'push button')
        buttonNamedPredicate = dogtail.predicate.IsAButtonNamed(
            dummyButton.name)
        self.assertTrue(buttonNamedPredicate.satisfiedByNode(dummyButton))
        self.assertEquals(buttonNamedPredicate.makeScriptMethodCall(
            False), u'button("dummy", recursive=False)')
        self.assertEquals(
            buttonNamedPredicate.makeScriptVariableName(), u'dummyButton')

    def test_predicates_page_tab_named(self):
        dummyTab = self.DummyNode('dummy', 'page tab')
        pageTabNamedPredicate = dogtail.predicate.IsATabNamed(dummyTab.name)
        self.assertTrue(pageTabNamedPredicate.satisfiedByNode(dummyTab))
        self.assertEquals(pageTabNamedPredicate.makeScriptMethodCall(
            False), u'tab("dummy", recursive=False)')
        self.assertEquals(
            pageTabNamedPredicate.makeScriptVariableName(), u'dummyTab')

    def test_predicates_generic_by_name(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        genericPredicateByName = dogtail.predicate.GenericPredicate(
            name=dn1.name)
        self.assertTrue(genericPredicateByName.satisfiedByNode(dn1))
        self.assertEquals(genericPredicateByName.makeScriptMethodCall(
            False), u'child( name="dummy name 1", recursive=False)')
        self.assertEquals(
            genericPredicateByName.makeScriptVariableName(), u'dummyName1Node')

    def test_predicates_generic_by_roleName(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        genericPredicateByRole = dogtail.predicate.GenericPredicate(
            roleName=dn1.roleName)
        self.assertTrue(genericPredicateByRole.satisfiedByNode(dn1))
        self.assertEquals(genericPredicateByRole.makeScriptMethodCall(
            False), u"child( roleName='dummy role 1', recursive=False)")
        self.assertEquals(
            genericPredicateByRole.makeScriptVariableName(), u'dummyRole1Node')

    def test_predicates_generic_by_description(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        genericPredicateByDescription = dogtail.predicate.GenericPredicate(
            description=dn1.description)
        self.assertTrue(genericPredicateByDescription.satisfiedByNode(dn1))
        self.assertEquals(genericPredicateByDescription.makeScriptMethodCall(
            False), u"child( description='dummy desc 1', recursive=False)")
        self.assertEquals(
            genericPredicateByDescription.makeScriptVariableName(), u'dummyDesc1Node')

    def test_predicates_generic_by_label(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        dn2 = self.DummyNode('dummy name 2', 'dummy role 2', 'dummy desc 2')
        dn2.labeller = dn1
        genericPredicateByLabel = dogtail.predicate.GenericPredicate(
            label=dn1.name)
        self.assertTrue(genericPredicateByLabel.satisfiedByNode(dn2))
        self.assertEquals(genericPredicateByLabel.makeScriptMethodCall(
            False), u'child(label="dummy name 1", recursive=False)')
        self.assertEquals(
            genericPredicateByLabel.makeScriptVariableName(), u'dummyName1Node')

    def test_predicates_named(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        genericNamedPredicate = dogtail.predicate.IsNamed(dn1.name)
        self.assertTrue(genericNamedPredicate.satisfiedByNode(dn1))
        self.assertEquals(genericNamedPredicate.makeScriptMethodCall(
            False), u'child(name="dummy name 1", recursive=False)')
        self.assertEquals(
            genericNamedPredicate.makeScriptVariableName(), u'dummyName1Node')

    def test_predicates_labelled_as(self):
        dn1 = self.DummyNode('dummy name 1', 'dummy role 1', 'dummy desc 1')
        dn2 = self.DummyNode('dummy name 2', 'dummy role 2', 'dummy desc 2')
        dn2.labeller = dn1
        genericLabelledPredicate = dogtail.predicate.IsLabelledAs(dn1.name)
        self.assertTrue(genericLabelledPredicate.satisfiedByNode(dn2))
        self.assertFalse(genericLabelledPredicate.satisfiedByNode(dn1))
        self.assertEquals(genericLabelledPredicate.makeScriptMethodCall(
            False), u'child(label="dummy name 1", recursive=False)')
        self.assertEquals(
            genericLabelledPredicate.makeScriptVariableName(), u'dummyName1Node')

    def test_predicates_dialog_named(self):
        dn1 = self.DummyNode('dummy name 1', 'dialog', 'dummy desc 1')
        genericNamedPredicate = dogtail.predicate.IsADialogNamed(dn1.name)
        self.assertTrue(genericNamedPredicate.satisfiedByNode(dn1))
        self.assertEquals(genericNamedPredicate.makeScriptMethodCall(
            False), u'dialog("dummy name 1")')
        self.assertEquals(
            genericNamedPredicate.makeScriptVariableName(), u'dummyName1Dlg')
