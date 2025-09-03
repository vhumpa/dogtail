#!/usr/bin/python3
"""
Unit tests for the dogtail.predicate.
"""

import unittest
import dogtail.tree
import dogtail.predicate


class DummyNode:
    """
    Dummy class to represent basic dogtail Node.
    """

    def __init__(self, name=None, role_name=None, description=None):
        self.name = name
        self.role_name = role_name
        self.description = description
        self.labeler = None
        self.text = "dummy text"


class TestPredicate(unittest.TestCase):
    """
    Class to test Predicate.
    """

    def test_correct_equality(self):
        """
        Test to make sure the predicate equal comparison is working.
        """

        predicate_1 = dogtail.predicate.GenericPredicate()
        predicate_2 = dogtail.predicate.GenericPredicate()

        self.assertEqual(predicate_1, predicate_2)


    def test_incorrect_equality(self):
        """
        Test to make sure the predicate unequal comparison is working.
        """

        predicate_1 = dogtail.predicate.GenericPredicate()

        self.assertNotEqual(predicate_1, self)


    def test_predicate_application(self):
        """
        Test Predicate IsAnApplicationNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="application")
        predicate = dogtail.predicate.IsAnApplicationNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_application_negation(self):
        """
        Test Predicate IsAnApplicationNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_application")
        predicate = dogtail.predicate.IsAnApplicationNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_tab(self):
        """
        Test Predicate IsATabNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="tab")
        predicate = dogtail.predicate.IsATabNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_tab_negation(self):
        """
        Test Predicate IsATabNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_tab")
        predicate = dogtail.predicate.IsATabNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_button(self):
        """
        Test Predicate IsAButtonNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="button")
        predicate = dogtail.predicate.IsAButtonNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_push_button(self):
        """
        Test Predicate IsAPushButtonNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="push button")
        predicate = dogtail.predicate.IsAPushButtonNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_button_negation(self):
        """
        Test Predicate IsAButtonNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_push_button")
        predicate = dogtail.predicate.IsAButtonNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_text(self):
        """
        Test Predicate IsATextEntryNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="text")
        predicate = dogtail.predicate.IsATextEntryNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_text_negation(self):
        """
        Test Predicate IsATextEntryNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_text")
        predicate = dogtail.predicate.IsATextEntryNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_menu_item(self):
        """
        Test Predicate IsAMenuItemNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="menu item")
        predicate = dogtail.predicate.IsAMenuItemNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_menu_item_negation(self):
        """
        Test Predicate IsAMenuItemNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_menu_item")
        predicate = dogtail.predicate.IsAMenuItemNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_menu(self):
        """
        Test Predicate IsAMenuNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="menu")
        predicate = dogtail.predicate.IsAMenuNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_menu_negation(self):
        """
        Test Predicate IsAMenuNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_menu")
        predicate = dogtail.predicate.IsAMenuNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_label_by_name(self):
        """
        Test Predicate IsLabelledAs.
        """

        dummy_application_1 = DummyNode(name="dummy_1", role_name="menu")
        dummy_application_2 = DummyNode(name="dummy_2", role_name="menu")

        dummy_application_2.labeler = dummy_application_1

        predicate = dogtail.predicate.IsLabelledAs(dummy_application_1.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application_2))


    def test_predicate_label_by_text(self):
        """
        Test Predicate IsLabelledAs.
        """

        dummy_application_1 = DummyNode(name="dummy_1", role_name="menu")
        dummy_application_1.text = "dummy_3"
        dummy_application_2 = DummyNode(name="dummy_2", role_name="menu")
        dummy_application_3 = DummyNode(name="dummy_3", role_name="menu")

        dummy_application_2.labeler = dummy_application_1

        predicate = dogtail.predicate.IsLabelledAs(dummy_application_3.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application_2))


    def test_predicate_label_negation(self):
        """
        Test Predicate IsLabelledAs False Result.
        """

        dummy_application_1 = DummyNode(name="dummy_1", role_name="menu")
        dummy_application_2 = DummyNode(name="dummy_2", role_name="menu")

        dummy_application_2.labeler = dummy_application_1

        predicate = dogtail.predicate.IsLabelledAs(dummy_application_1.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application_1))


    def test_predicate_dialog(self):
        """
        Test Predicate IsADialogNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="dialog")
        predicate = dogtail.predicate.IsADialogNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_dialog_negation(self):
        """
        Test Predicate IsADialogNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_dialog")
        predicate = dogtail.predicate.IsADialogNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_window(self):
        """
        Test Predicate IsAWindow.
        """

        dummy_application = DummyNode(name="dummy", role_name="window")
        predicate = dogtail.predicate.IsAWindow()

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_window_negation(self):
        """
        Test Predicate IsAWindow False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_window")
        predicate = dogtail.predicate.IsAWindow()

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_window_named(self):
        """
        Test Predicate IsAWindowNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="window")
        predicate = dogtail.predicate.IsAWindowNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_window_named_negation(self):
        """
        Test Predicate IsAWindowNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_window")
        predicate = dogtail.predicate.IsAWindowNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_frame_named(self):
        """
        Test Predicate IsAFrameNamed.
        """

        dummy_application = DummyNode(name="dummy", role_name="frame")
        predicate = dogtail.predicate.IsAFrameNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_frame_named_negation(self):
        """
        Test Predicate IsAFrameNamed False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_frame")
        predicate = dogtail.predicate.IsAFrameNamed(dummy_application.name)

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_frame_named_name_negation(self):
        """
        Test Predicate IsAFrameNamed Name False Result.
        """

        dummy_application = DummyNode(name="dummy", role_name="not_frame")
        predicate = dogtail.predicate.IsAFrameNamed("not_dummy")

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_frame_named_name_negation_frame_correction(self):
        """
        Test Predicate IsAFrameNamed Name False Result Frame Correct.
        """

        dummy_application = DummyNode(name="dummy", role_name="frame")
        predicate = dogtail.predicate.IsAFrameNamed("not_dummy")

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_predicate_named(self):
        """
        Test Predicate IsNamed.
        """

        dummy_application = DummyNode(name="dummy")
        predicate = dogtail.predicate.IsNamed(dummy_application.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_predicate_named_negation(self):
        """
        Test Predicate IsNamed False Result.
        """

        dummy_application = DummyNode(name="dummy")
        predicate = dogtail.predicate.IsNamed("not_dummy")

        self.assertFalse(predicate.satisfied_by_node(dummy_application))


    def test_generic_predicate_by_name(self):
        """
        Test Predicate GenericPredicate by Name.
        """

        dummy_application = DummyNode(name="dummy")
        predicate = dogtail.predicate.GenericPredicate(name="dummy")

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_generic_predicate_by_role_name(self):
        """
        Test Predicate GenericPredicate by Role Name.
        """

        dummy_application = DummyNode(role_name="dummy role name")
        predicate = dogtail.predicate.GenericPredicate(role_name="dummy role name")

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_generic_predicate_by_description(self):
        """
        Test Predicate GenericPredicate by Description.
        """

        dummy_application = DummyNode(description="dummy description")
        predicate = dogtail.predicate.GenericPredicate(description="dummy description")

        self.assertTrue(predicate.satisfied_by_node(dummy_application))


    def test_generic_predicate_by_label(self):
        """
        Test Predicate GenericPredicate by label.
        """

        dummy_application_1 = DummyNode(name="dummy_1", role_name="menu")
        dummy_application_2 = DummyNode(name="dummy_2", role_name="menu")

        dummy_application_2.labeler = dummy_application_1

        predicate = dogtail.predicate.GenericPredicate(label=dummy_application_1.name)

        self.assertTrue(predicate.satisfied_by_node(dummy_application_2))


if __name__ == "__main__":
    unittest.main()
