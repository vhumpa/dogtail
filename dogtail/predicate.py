#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release. Simple Predicate
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# ruff: noqa: E402

# TODO To be change to dogtail.logging before release.
from dogtail._logging import logging_class
LOGGER = logging_class.logger

class GenericPredicate:
    """
    Simple predicate class, providing easy way to compare nodes.
    """

    def __init__(self, name=None, role_name=None, description=None, label=None):
        self.name = name
        self.role_name = role_name
        self.description = description
        self.label = label
        self.satisfied_by_node = self._get_compare_function()


    def _get_compare_function(self):
        def predicate_satisfied_by_node(node):
            """
            Simple comparison function that can be used in case of non-lambda search.

            :param node: Accessible object.
            :type node: Atspi.Accessible

            :return: True or False based on given criteria.
            :rtype: bool
            """

            # First lets check if user wants to check label.
            if self.label:
                # If so, check if labeler labeler is present.
                if node.labeler:
                    # Try to match either text or name of the labeler.
                    label_name = self.label == node.labeler.name
                    label_text = self.label == node.labeler.text
                    return label_name or label_text
                # No labeler, match is False.
                return False

            try:
                # Check if user wants to check name.
                if self.name:
                    # Compare name of self with the given node.
                    if self.name != node.name:
                        return False

                # Check if user wants to check role_name.
                if self.role_name:
                    # Compare role_name of self with the given node.
                    if self.role_name != node.role_name:
                        return False

                # Check if user wants to check description.
                if self.description:
                    # Compare description of self with the given node.
                    if self.description != node.description:
                        return False

                # There are no conflicting parameters, match is a success.
                return True

            except Exception:
                return False

        return predicate_satisfied_by_node
