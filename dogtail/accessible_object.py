#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# ruff: noqa: E402
# ruff: noqa: E501

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from types import LambdaType
from _simple_predicate import SimplePredicate

# TODO To be change to dogtail.logging before release.
from _logging import logging_class
LOGGING = logging_class.logger


class AccessibleObject:
    """
    Utility class for obtaining information about Accessible Objects.
    Heavily inspired by Orca's AXObject.
    """

    @staticmethod
    def is_newton(acc_object):  # pylint: disable=unused-argument
        """
        Returns True if an accessible object is Newton.
        For now lets just prepare it before having hands on experience.
        """

        return False
        #return isinstance(acc_object, newton_atspi_compat.Accessible)


    @staticmethod
    def is_valid(acc_object):
        """
        Returns False if we know for certain this object is invalid.
        """

        return acc_object is not None


    @staticmethod
    def is_action(acc_object):
        """
        Return True if Atspi object is an Action else False.
        """

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_action_iface() is not None

        return Atspi.Accessible.get_action_iface(acc_object) is not None


    @staticmethod
    def is_text(acc_object):
        """
        Return True if Atspi object is an Text else False.
        """

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_text_iface() is not None

        return Atspi.Accessible.get_text_iface(acc_object) is not None


    @staticmethod
    def is_editable_text(acc_object):
        """
        Return True if Atspi object is an EditableText else False.
        """

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_editable_text_iface() is not None

        return Atspi.Accessible.get_editable_text_iface(acc_object) is not None


    @staticmethod
    def is_component(acc_object):
        """
        Return True if Atspi object is a Component else False.
        """

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_component_iface() is not None

        return Atspi.Accessible.get_component_iface(acc_object) is not None


    @staticmethod
    def is_selection(acc_object):
        """
        Return True if Atspi object is an EditableText else False.
        """

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_selection_iface() is not None

        return Atspi.Accessible.get_selection_iface(acc_object) is not None


    @staticmethod
    def is_value(acc_object):
        """
        Return True if Atspi object is an Value else False.
        """

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_value_iface() is not None

        return Atspi.Accessible.get_value_iface(acc_object) is not None


    @staticmethod
    def iter_children(acc_object, pred=None):
        """
        Generator to iterate through object's children. If the function pred is
        specified, children for which pred is False will be skipped.
        """

        if not AccessibleObject.is_valid(acc_object):
            return

        child_count = AccessibleObject.get_child_count(acc_object)
        for index in range(child_count):
            child = AccessibleObject.get_child_at_index(acc_object, index)
            if child is not None and (pred is None or pred(child)):
                yield child


    @staticmethod
    def get_child_at_index(acc_object, index):
        """
        Returns the nth child of obj.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        n_children = AccessibleObject.get_child_count(acc_object)
        if n_children <= 0:
            return None

        if index == -1:
            index = n_children - 1

        if not 0 <= index < n_children:
            return None

        try:

            if AccessibleObject.is_newton(acc_object):
                child = acc_object.get_child_at_index(index)
            else:
                child = Atspi.Accessible.get_child_at_index(acc_object, index)

        except Exception as error:
            LOGGING.info(f"Exception when getting child at index: '{error}'")
            return None

        if child == acc_object:
            LOGGING.info(f"Object '{acc_object}' claims to be its own child.")
            return None

        return child


    @staticmethod
    def get_child_count(acc_object):
        """
        Returns number of children in given object.
        """

        if not AccessibleObject.is_valid(acc_object):
            return 0

        try:
            if AccessibleObject.is_newton(acc_object):
                count = acc_object.get_child_count()
            else:
                count = Atspi.Accessible.get_child_count(acc_object)

        except Exception as error:
            LOGGING.info(f"Exception when getting child count: '{error}'")
            return 0

        return count


    @staticmethod
    def _find_all_descendants(acc_object, predicate, matches):
        """
        Returns all descendants that match a predicate.
        """

        if not AccessibleObject.is_valid(acc_object):
            return

        child_count = AccessibleObject.get_child_count(acc_object)
        for index in range(child_count):
            child = AccessibleObject.get_child_at_index(acc_object, index)
            if predicate and predicate(child):
                matches.append(child)

            AccessibleObject._find_all_descendants(child, predicate, matches)


    @staticmethod
    def find_all_descendants(acc_obj, given_predicate):
        """
        Returns all descendants that match a predicate.
        """

        # User is using lambdas.
        if isinstance(given_predicate, LambdaType):
            predicate = given_predicate
        # User is using a SimplePredicate.
        elif isinstance(given_predicate, SimplePredicate):
            predicate = given_predicate.satisfied_by_node
        # Unknown/unsupported way to compare nodes.
        else:
            LOGGING.info("Unknown/unsupported way to compare nodes.")
            return None

        matches = []
        AccessibleObject._find_all_descendants(acc_obj, predicate, matches)
        return matches


    @staticmethod
    def find_descendant(acc_obj, given_predicate, depth_first=True):
        """
        Find a single descendant node satisfying the predicate.
        """

        # User is using lambdas.
        if isinstance(given_predicate, LambdaType):
            predicate = given_predicate
        # User is using a SimplePredicate.
        elif isinstance(given_predicate, SimplePredicate):
            predicate = given_predicate.satisfied_by_node
        # Unknown/unsupported way to compare nodes.
        else:
            LOGGING.info("Unknown/unsupported way to compare nodes.")
            return None

        if depth_first:
            success_match = AccessibleObject._find_descendant_depth_first(acc_obj, predicate)
        else:  # breadth_first
            success_match = AccessibleObject._find_descendant_breadth_first(acc_obj, predicate)

        return success_match


    @staticmethod
    def _find_descendant_depth_first(acc_object, pred):
        """
        Find a single descendant node satisfying the predicate, searching depth first.
        """

        try:
            if pred(acc_object):
                return acc_object
        except Exception:
            pass

        for child in acc_object:
            try:
                success_match = AccessibleObject._find_descendant_depth_first(child, pred)
            except Exception:
                success_match = None

            if success_match is not None:
                return success_match

        return


    @staticmethod
    def _find_descendant_breadth_first(acc_object, pred):
        """
        Find a single descendant node satisfying the predicate, searching breadth first.
        """

        for child in acc_object:
            try:
                if pred(acc_object):
                    return acc_object
            except Exception:
                pass

        for child in acc_object:
            try:
                success_match = AccessibleObject._find_descendant_breadth_first(child, pred)
            except Exception:
                success_match = None

            if success_match is not None:
                return success_match

        return


    @staticmethod
    def find_ancestor(acc_object, pred):
        """
        Find a single ancestor satisfying the predicate.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        # Keep track of objects we've encountered in order to handle broken trees.
        objects = [acc_object]
        parent = AccessibleObject.get_parent_checked(acc_object)
        while parent:
            if parent in objects:
                LOGGING.info(f"Circular tree suspected, {parent} was found already.")
                return None

            if pred(parent):
                return parent

            objects.append(parent)
            parent = AccessibleObject.get_parent_checked(parent)

        return None


    @staticmethod
    def get_parent_checked(acc_object):
        """
        Returns the parent of obj, doing checks for tree validity.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            role = Atspi.Role(acc_object.get_role())
        else:
            role = Atspi.Accessible.get_role(acc_object)

        role = acc_object.get_role
        if role in [Atspi.Role.INVALID, Atspi.Role.APPLICATION]:
            return None

        parent = acc_object.parent
        if parent is None:
            return None

        return parent


    @staticmethod
    def get_process_id(acc_object):
        """
        Returns the pid associated with the obj.
        """

        if not AccessibleObject.is_valid(acc_object):
            return -1

        try:
            if AccessibleObject.is_newton(acc_object):
                process_id = acc_object.get_process_id()
            else:
                process_id = Atspi.Accessible.get_process_id(acc_object)

        except Exception as error:
            LOGGING.info(f"Exception when getting process id: '{error}'")
            return -1

        return process_id


    @staticmethod
    def get_name(acc_object):
        """
        Returns a 'name' for Accessible object.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_name()

        return Atspi.Accessible.get_name(acc_object)


    @staticmethod
    def get_role(acc_object):
        """
        Returns a 'role' for Accessible object.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_role()

        return Atspi.Accessible.get_role(acc_object)


    @staticmethod
    def get_role_name(acc_object):
        """
        Returns a 'role_name' for Accessible object.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_role_name()

        return Atspi.Accessible.get_role_name(acc_object)


    @staticmethod
    def get_description(acc_object):
        """
        Returns a 'description' for Accessible object.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_description()

        return Atspi.Accessible.get_description(acc_object)


    @staticmethod
    def get_parent(acc_object):
        """
        Returns a 'parent' for Accessible object.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_parent()

        return Atspi.Accessible.get_parent(acc_object)


    @staticmethod
    def get_index_in_parent(acc_object):
        """
        Returns a 'index_in_parent' for Accessible object.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        # Default value if object has no containing parent or exception happened.
        final_index = -1

        if AccessibleObject.is_newton(acc_object):
            final_index = acc_object.get_index_in_parent()
        else:
            final_index = Atspi.Accessible.get_index_in_parent(acc_object)

        # Not working as expected sometimes. Working around it.
        if final_index == -1:
            LOGGING.info("Error in get_index_in_parent. Attempting to work around.")

            for index, child in enumerate(acc_object.parent.children):
                if child.parent.get_child_at_index(index) == acc_object:
                    LOGGING.info(f"Success, index was: '{index}'")
                    return index

        return final_index


    @staticmethod
    def get_children(acc_object):
        """
        Returns a 'parent' for Accessible object.
        """

        if not AccessibleObject.is_valid(acc_object):
            return None

        children_list = []

        for index in range(AccessibleObject.get_child_count(acc_object)):
            child = AccessibleObject.get_child_at_index(acc_object, index)
            if child:
                children_list.append(child)

        return children_list


    @staticmethod
    def get_labeler(acc_object):
        """
        'labeller' (read-only list of Node instances):
        The node(s) that is/are a label for this node. Generated from 'relations'.
        """

        if not AccessibleObject.is_valid(acc_object):
            return []

        targets = set()

        if AccessibleObject.is_newton(acc_object):
            relation_set = acc_object.get_relation_set()
        else:
            relation_set = Atspi.Accessible.get_relation_set(acc_object)

        for relation in relation_set:

            if AccessibleObject.is_newton(acc_object):
                relation_type = None # TODO, learn how Newton defines it.
            else:
                relation_type =  Atspi.RelationType.LABELLED_BY

            if relation.get_relation_type() == relation_type:
                if relation.get_n_targets() == 1:
                    return relation.get_target(0)

                # Using set to avoid duplicates.
                for i in range(relation.get_n_targets()):
                    targets.add(relation.get_target(i))
                return targets

        # Convert set to list.
        return list(targets)


    @staticmethod
    def get_labelee(acc_object):
        """
        'labelee' (read-only list of Node instances):
        The node(s) that this node is a label for. Generated from 'relations'.
        """

        if not AccessibleObject.is_valid(acc_object):
            return []

        targets = set()

        if AccessibleObject.is_newton(acc_object):
            relation_set = acc_object.get_relation_set()
        else:
            relation_set = Atspi.Accessible.get_relation_set(acc_object)

        for relation in relation_set:

            if AccessibleObject.is_newton(acc_object):
                relation_type = None # TODO, learn how Newton defines it.
            else:
                relation_type =  Atspi.RelationType.LABEL_FOR

            if relation.get_relation_type() == relation_type:
                if relation.get_n_targets() == 1:
                    return relation.get_target(0)

                # Using set to avoid duplicates.
                for i in range(relation.get_n_targets()):
                    targets.add(relation.get_target(i))
                return targets

        # Convert set to list.
        return list(targets)
