#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# ruff: noqa: E402
# ruff: noqa: E501

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from types import LambdaType
import inspect
from dogtail.predicate import GenericPredicate
from dogtail.config import config
from dogtail.utils import do_delay

from dogtail.logging import logging_class
LOGGING = logging_class.logger

# TODO think about logging and how much of it we need to not get flooded.
# Most likely will do 2 levels, debug and debug_verbose and check method by method.


class SearchError(Exception):
    """
    The widget was not found.
    """


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

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return False
        #return isinstance(acc_object, newton_atspi_compat.Accessible)


    @staticmethod
    def is_dead(acc_object):
        """
        Returns True if we know for certain this object is not valid.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        # Either empty or not Atspi.Accessible type.
        if not AccessibleObject.is_valid(acc_object):
            return True

        # Good indicator of dead object, no children and no parent.
        empty_children_list = AccessibleObject.get_children(acc_object) == []
        no_parent = AccessibleObject.get_parent(acc_object) is None
        if empty_children_list and no_parent:
            return True

        return False


    @staticmethod
    def is_valid(acc_object):
        """
        Returns False if we know for certain this object is invalid.
        """

        # TODO verbose logging? This will flood logs, perhaps too much even for verbose.
        #LOGGING.debug(logging_class.get_func_params_and_values())

        return acc_object is not None and isinstance(acc_object, Atspi.Accessible)


    @staticmethod
    def is_action(acc_object):
        """
        Return True if Atspi object is an Action else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_action_iface() is not None

        return Atspi.Accessible.get_action_iface(acc_object) is not None


    @staticmethod
    def is_text(acc_object):
        """
        Return True if Atspi object is an Text else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_text_iface() is not None

        return Atspi.Accessible.get_text_iface(acc_object) is not None


    @staticmethod
    def is_editable_text(acc_object):
        """
        Return True if Atspi object is an EditableText else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_editable_text_iface() is not None

        return Atspi.Accessible.get_editable_text_iface(acc_object) is not None


    @staticmethod
    def is_hypertext(acc_object):
        """
        Return True if Atspi object is an Hypertext else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_hypertext_iface() is not None

        return Atspi.Accessible.get_hypertext_iface(acc_object) is not None


    @staticmethod
    def is_image(acc_object):
        """
        Return True if Atspi object is an Image else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_image_iface() is not None

        return Atspi.Accessible.get_image_iface(acc_object) is not None


    @staticmethod
    def is_component(acc_object):
        """
        Return True if Atspi object is a Component else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_component_iface() is not None

        return Atspi.Accessible.get_component_iface(acc_object) is not None


    @staticmethod
    def is_selection(acc_object):
        """
        Return True if Atspi object is an Selection else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_selection_iface() is not None

        return Atspi.Accessible.get_selection_iface(acc_object) is not None


    @staticmethod
    def is_table(acc_object):
        """
        Return True if Atspi object is an Table else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_table_iface() is not None

        return Atspi.Accessible.get_table_iface(acc_object) is not None


    @staticmethod
    def is_value(acc_object):
        """
        Return True if Atspi object is an Value else False.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_value_iface() is not None

        return Atspi.Accessible.get_value_iface(acc_object) is not None


    @staticmethod
    def iter_children(acc_object, pred=None):
        """
        Generator to iterate through object's children. If the function pred is
        specified, children for which pred is False will be skipped.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

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
            LOGGING.debug(f"Exception when getting child at index: '{error}'")
            return None

        if child == acc_object:
            LOGGING.debug(f"Object '{acc_object}' claims to be its own child.")
            return None

        return child


    @staticmethod
    def get_child_count(acc_object):
        """
        Returns number of children in given object.
        """

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return 0

        try:
            if AccessibleObject.is_newton(acc_object):
                count = acc_object.get_child_count()
            else:
                count = Atspi.Accessible.get_child_count(acc_object)

        except Exception as error:
            LOGGING.debug(f"Exception when getting child count: '{error}'")
            return 0

        return count


    @staticmethod
    def _find_all_descendants(acc_object, predicate, matches):
        """
        Returns all descendants that match a predicate.
        """

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return

        child_count = AccessibleObject.get_child_count(acc_object)
        for index in range(child_count):
            child = AccessibleObject.get_child_at_index(acc_object, index)
            try:
                if predicate and predicate(child):
                    matches.append(child)
            except Exception as error:
                LOGGING.debug(f"Exception occurred in predicate match '{error}'.")

            AccessibleObject._find_all_descendants(child, predicate, matches)


    @staticmethod
    def find_all_descendants(acc_object, given_predicate, **kwargs):
        """
        Returns all descendants that match a predicate.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        # Pull values from kwargs here.
        validated_recursive = True
        validated_showing_only = config.search_showing_only
        # ===================================================
        for key, val in kwargs.items():
            if "recursive" == str(key):
                validated_recursive = val

            if str(key) in ("showingOnly", "showing_only"):
                validated_showing_only = val
        # ===================================================

        # User is using lambdas.
        if isinstance(given_predicate, LambdaType):
            predicate = given_predicate

            # Showing only handling.
            if validated_showing_only:
                def extend_predicate(x):
                    return predicate(x) and x.showing
                predicate = extend_predicate

        # User is using a GenericPredicate.
        elif isinstance(given_predicate, type(GenericPredicate())):
            # Showing only handling for predicates.
            given_predicate.showing_only = validated_showing_only

            predicate = given_predicate.satisfied_by_node

        # Unknown/unsupported way to compare nodes.
        else:
            LOGGING.info("Unknown/unsupported way to compare nodes.")
            return None

        matches = []
        if not validated_recursive:
            list(filter(predicate, acc_object.children))

        else:
            AccessibleObject._find_all_descendants(acc_object, predicate, matches)
        return matches


    @staticmethod
    def find_descendant(acc_object, given_predicate, depth_first=True, **kwargs):
        """
        Find a single descendant node satisfying the predicate.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        # Pull values from kwargs here.
        validated_retry = True
        validated_recursive = True
        validated_require_result = True
        validated_showing_only = config.search_showing_only
        # ===================================================
        for key, val in kwargs.items():
            if "retry" == str(key):
                validated_retry = val

            if "recursive" == str(key):
                validated_recursive = val

            if str(key) in ("requireResult", "require_result"):
                validated_require_result = val

            if str(key) in ("showingOnly", "showing_only"):
                validated_showing_only = val
        # ===================================================

        # User is using lambdas.
        if isinstance(given_predicate, LambdaType):
            predicate = given_predicate

            _description = inspect.getsource(predicate).strip("\n")
            formatted_description = _description.replace("  ", "").replace("\n", " ")
            description_to_use = formatted_description

            # Showing only handling.
            if validated_showing_only:
                def extend_predicate(x):
                    return predicate(x) and x.showing
                predicate = extend_predicate
                description_to_use += " and x.showing"

        # User is using a GenericPredicate.
        elif isinstance(given_predicate, type(GenericPredicate())):
            # Showing only handling for predicates.
            given_predicate.showing_only = validated_showing_only

            predicate = given_predicate.satisfied_by_node

            description_to_use = str(given_predicate)

        # Unknown/unsupported way to compare nodes.
        else:
            predicate_type = type(given_predicate)
            LOGGING.info(f"Unknown/unsupported way '{predicate_type}' to compare nodes.")
            raise SearchError("No match.")

        # Debug description of what user is searching for.
        LOGGING.debug(f"Searching for '{description_to_use}'")

        for number_of_attempts in range(1, config.search_cut_off_limit + 1):
            if number_of_attempts >= config.search_warning_threshold or config.debug_searching:
                LOGGING.info(f"Searching again (attempt '{number_of_attempts}')")

            try:
                if not validated_recursive:
                    success_match = next(filter(predicate, acc_object.children), None)

                elif depth_first:
                    success_match = AccessibleObject._find_descendant_depth_first(acc_object, predicate)

                else:  # breadth_first
                    success_match = AccessibleObject._find_descendant_breadth_first(acc_object, predicate)

                if success_match:
                    return success_match

                if not validated_retry:
                    break

            except GLib.GError as error:
                if number_of_attempts == config.search_cut_off_limit:
                    LOGGING.info(f"GLib Error caught from a11y tree: '{error}'")
                    raise RuntimeError(" ".join((
                        "Error: Session has probably broken a11y!",
                        "Exiting allowing session re-runs",
                    ))) from error

                do_delay(config.search_back_off_delay)

            except TypeError as error:
                LOGGING.info(f"Unexpected TypeError from a11y tree search: '{error}'")
                do_delay(config.search_back_off_delay)

            do_delay(config.search_back_off_delay)

        if validated_require_result:
            raise SearchError(f"No match for '{description_to_use}'")


    @staticmethod
    def _find_descendant_depth_first(acc_object, pred):
        """
        Find a single descendant node satisfying the predicate, searching depth first.
        """

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

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

        return None


    @staticmethod
    def _find_descendant_breadth_first(acc_object, pred):
        """
        Find a single descendant node satisfying the predicate, searching breadth first.
        """

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

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

        return None


    @staticmethod
    def find_ancestor(acc_object, given_predicate, **kwargs):
        """
        Find a single ancestor satisfying the predicate.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        # Pull values from kwargs here.
        validated_retry = True
        validated_require_result = True
        validated_showing_only = config.search_showing_only
        # ===================================================
        for key, val in kwargs.items():
            if "retry" == str(key):
                validated_retry = val

            if str(key) in ("requireResult", "require_result"):
                validated_require_result = val

            if str(key) in ("showingOnly", "showing_only"):
                validated_showing_only = val
        # ===================================================

        # User is using lambdas.
        if isinstance(given_predicate, LambdaType):
            predicate = given_predicate

            _description = inspect.getsource(predicate).strip("\n")
            formatted_description = _description.replace("  ", "").replace("\n", " ")
            description_to_use = formatted_description

            # Showing only handling.
            if validated_showing_only:
                def extend_predicate(x):
                    return predicate(x) and x.showing
                predicate = extend_predicate
                description_to_use += " and x.showing"

        # User is using a GenericPredicate.
        elif isinstance(given_predicate, type(GenericPredicate())):
            # Showing only handling for predicates.
            given_predicate.showing_only = validated_showing_only

            predicate = given_predicate.satisfied_by_node

            description_to_use = str(given_predicate)

        # Unknown/unsupported way to compare nodes.
        else:
            predicate_type = type(given_predicate)
            LOGGING.info(f"Unknown/unsupported way '{predicate_type}' to compare nodes.")
            raise SearchError("No match.")

        # Debug description of what user is searching for.
        LOGGING.debug(f"Searching for '{description_to_use}'")

        # Keep track of objects we've encountered in order to handle broken trees.

        for number_of_attempts in range(1, config.search_cut_off_limit + 1):
            if number_of_attempts >= config.search_warning_threshold or config.debug_searching:
                LOGGING.info(f"Searching again (attempt '{number_of_attempts}')")

            try:
                objects = [acc_object]
                parent = AccessibleObject.get_parent_checked(acc_object)
                while parent:
                    if parent in objects:
                        LOGGING.debug(f"Circular tree suspected, {parent} was found already.")
                        return None

                    if predicate(parent):
                        return parent

                    objects.append(parent)
                    parent = AccessibleObject.get_parent_checked(parent)

                if not validated_retry:
                    break

            except GLib.GError as error:
                if number_of_attempts == config.search_cut_off_limit:
                    LOGGING.info(f"GLib Error caught from a11y tree: '{error}'")
                    raise RuntimeError(" ".join((
                        "Error: Session has probably broken a11y!",
                        "Exiting allowing session re-runs",
                    ))) from error

                do_delay(config.search_back_off_delay)

            except TypeError as error:
                LOGGING.info(f"Unexpected TypeError from a11y tree search: '{error}'")
                do_delay(config.search_back_off_delay)

            do_delay(config.search_back_off_delay)

        if validated_require_result:
            raise SearchError(f"No match for '{description_to_use}'")

        return None

    @staticmethod
    def get_parent_checked(acc_object):
        """
        Returns the parent of obj, doing checks for tree validity.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return -1

        try:
            if AccessibleObject.is_newton(acc_object):
                process_id = acc_object.get_process_id()
            else:
                process_id = Atspi.Accessible.get_process_id(acc_object)

        except Exception as error:
            LOGGING.debug(f"Exception when getting process id: '{error}'")
            return -1

        return process_id


    @staticmethod
    def get_id(acc_object):
        """
        Returns a 'id' for Accessible object.
        """

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_id()

        try:
            return Atspi.Accessible.get_id(acc_object)
        except Exception as error:
            raise RuntimeError("Get Id function failed.") from error


    @staticmethod
    def get_name(acc_object):
        """
        Returns a 'name' for Accessible object.
        """

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            return acc_object.get_name()

        try:
            return Atspi.Accessible.get_name(acc_object)
        except Exception as error:
            raise RuntimeError("Get Name function failed.") from error


    @staticmethod
    def get_role(acc_object):
        """
        Returns a 'role' for Accessible object.
        """

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

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

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

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

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

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

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

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

        LOGGING.debug(logging_class.get_func_params_and_values())

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
            LOGGING.debug("Error in get_index_in_parent. Attempting to work around.")

            for index, child in enumerate(acc_object.parent.children):
                if child.parent.get_child_at_index(index) == acc_object:
                    LOGGING.debug(f"Success, index was: '{index}'")
                    return index

        return final_index


    @staticmethod
    def get_attributes(acc_object):
        """
        Returns 'attributes' for Accessible object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            attributes = acc_object.get_attributes()
        else:
            attributes = Atspi.Accessible.get_attributes(acc_object)

        return attributes


    @staticmethod
    def get_attributes_as_array(acc_object):
        """
        Returns 'attributes_as_array' for Accessible object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            attributes_as_array = acc_object.get_attributes_as_array()
        else:
            attributes_as_array = Atspi.Accessible.get_attributes_as_array(acc_object)

        return attributes_as_array


    @staticmethod
    def get_children(acc_object):
        """
        Returns a 'parent' for Accessible object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            # TODO Newton
            return []
        else:
            children_list = []

            for index in range(AccessibleObject.get_child_count(acc_object)):
                child = AccessibleObject.get_child_at_index(acc_object, index)
                if child:
                    children_list.append(child)

            return children_list


    @staticmethod
    def is_last_child(acc_object):
        """
        Returns a 'parent' for Accessible object.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        if not AccessibleObject.is_valid(acc_object):
            return None

        if AccessibleObject.is_newton(acc_object):
            return False # TODO
        else:
            does_not_have_parent = not AccessibleObject.get_parent(acc_object)
            index_in_parent_is_not_valid = AccessibleObject.get_index_in_parent(acc_object) is None

            index_in_parent = AccessibleObject.get_index_in_parent(acc_object)
            child_count = AccessibleObject.get_parent(acc_object).get_child_count(acc_object) - 1

            is_last_index = index_in_parent == child_count

            return does_not_have_parent or index_in_parent_is_not_valid or is_last_index


    @staticmethod
    def get_labeler(acc_object):
        """
        'labeller' (read-only list of Node instances):
        The node(s) that is/are a label for this node. Generated from 'relations'.
        """

        # TODO verbose logging?
        #LOGGING.debug(logging_class.get_func_params_and_values())

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
                relation_type = Atspi.RelationType.LABELLED_BY

            if relation.get_relation_type() == relation_type:
                if relation.get_n_targets() == 1:
                    return relation.get_target(0)

                # Using set to avoid duplicates.
                for i in range(relation.get_n_targets()):
                    targets.add(relation.get_target(i))
                return list(targets)

        # Convert set to list.
        return list(targets)


    @staticmethod
    def get_labelee(acc_object):
        """
        'labelee' (read-only list of Node instances):
        The node(s) that this node is a label for. Generated from 'relations'.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

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
                relation_type = Atspi.RelationType.LABEL_FOR

            if relation.get_relation_type() == relation_type:
                if relation.get_n_targets() == 1:
                    return relation.get_target(0)

                # Using set to avoid duplicates.
                for i in range(relation.get_n_targets()):
                    targets.add(relation.get_target(i))
                return list(targets)

        # Convert set to list.
        return list(targets)
