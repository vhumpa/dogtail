#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release. Simple Predicate
"""

# pylint: disable=broad-exception-caught
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# ruff: noqa: E402
# ruff: noqa: E501

from dogtail.logging import logging_class
LOGGER = logging_class.logger


class GenericPredicate:
    """
    Simple predicate class, providing easy way to compare nodes.
    """

    def __init__(self, name=None, role_name=None, description=None, label=None, identifier=None, **kwargs):

        using_role_name = role_name
        # === Backward compatibility and extra parameters ===
        for key, val in kwargs.items():
            if "roleName" in str(key):
                using_role_name = val
        # ===================================================

        self.name = name
        self.role_name = using_role_name
        self.description = description
        self.label = label
        self.identifier = identifier
        self.showing_only = None
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
            if self.label is not None:
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
                if self.name is not None:
                    # Compare name of self with the given node.
                    if self.name != node.name:
                        return False

                # Check if user wants to check role_name.
                if self.role_name is not None:
                    # Compare role_name of self with the given node.
                    # If 'push button' is wanted, attempt to match also 'button'
                    if (self.role_name != "push button" and self.role_name != node.role_name) or (
                        self.role_name == "push button" and node.role_name not in ("button", "push button")
                    ):
                        return False

                # Check if user wants to check description.
                if self.description is not None:
                    # Compare description of self with the given node.
                    if self.description != node.description:
                        return False

                # Check if user wants to check identifier.
                if self.identifier is not None:
                    # The method get_attributes is from Atspi.Accessible.
                    atspi_accessible_attributes = node.get_attributes()

                    # Check if the wanted id's are present.
                    id_present = "id" in atspi_accessible_attributes
                    accessible_id_present = "accessibleID" in dir(node)

                    # Compare identifier with the given node's "id".
                    if id_present and self.identifier != atspi_accessible_attributes["id"]:
                        return False

                    # Compare identifier with the given node's "accessibleID".
                    elif accessible_id_present and self.identifier != node.accessibleID:
                        return False

                    # No "id" or "accessibleID to check against.
                    else:
                        return False

                # Check if user wants to match showing only.
                if self.showing_only:
                    # Compare description of self with the given node.
                    if not node.showing:
                        return False

                # There are no conflicting parameters, match is a success.
                return True

            except Exception:
                return False

        return predicate_satisfied_by_node


    def __eq__(self, other):
        """
        Predicates are considered equal if they are of the same subclass and have the
        same data.
        """

        if not isinstance(self, type(other)):
            return False

        # Since the compare function will have different hexadecimal,
        # lets remove it from the comparison.
        # predicate_satisfied_by_node at 0x7fdb99f787c0>
        # predicate_satisfied_by_node at 0x7fdb96683060>

        exclude_key = {"satisfied_by_node"}

        self_dict = {key: self.__dict__[key] for key in set(list(self.__dict__.keys())) - set(exclude_key)}
        other_dict = {key: other.__dict__[key] for key in set(list(other.__dict__.keys())) - set(exclude_key)}

        return self_dict == other_dict


    def __str__(self):
        """
        Representation of what the Predicate is matching.
        """

        string_to_represent_object = ""
        string_to_represent_object += f"name:{repr(self.name)} "
        string_to_represent_object += f"role_name:{repr(self.role_name)} "
        string_to_represent_object += f"description:{repr(self.description)} "
        string_to_represent_object += f"label:{repr(self.label)} "
        string_to_represent_object += f"id:{repr(self.identifier)} "
        string_to_represent_object += f"showing_only:{repr(self.showing_only)}"
        return string_to_represent_object


class IsAnApplicationNamed(GenericPredicate):
    """
    Predicate subclass that looks for a application by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="application")


class IsATabNamed(GenericPredicate):
    """
    Predicate subclass that looks for a tab by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="tab")


class IsAButtonNamed(GenericPredicate):
    """
    Predicate subclass that looks for a button by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="button")


class IsAPushButtonNamed(GenericPredicate):
    """
    Predicate subclass that looks for a push button by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="push button")


class IsATextEntryNamed(GenericPredicate):
    """
    Predicate subclass that looks for a text entry by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="text")

class IsAMenuItemNamed(GenericPredicate):
    """
    Predicate subclass that looks for a menu item by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="menu item")


class IsAMenuNamed(GenericPredicate):
    """
    Predicate subclass that looks for a menu by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="menu")


class IsLabelledBy(GenericPredicate):
    """
    Predicate: is this node labelled by another node.
    """

    # I do not see a reason for this.
    # If user wants to know that something has a labeller, who not just ask <>.labeller?
    # This was empty in older version of dogtail, so what did it do?


class IsLabelledAs(GenericPredicate):
    """
    Predicate: is this node labelled with the text string (i.e. by another node with
    that as a name).
    """

    def __init__(self, label=None):
        self.label = label

        if not self.label:
            LOGGER.info("You did not provide any 'label' to match.")
            self.label = "__invalid__"

        super().__init__(label=self.label)


class IsADialogNamed(GenericPredicate):
    """
    Predicate subclass that looks for a top-level dialog by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="dialog")


class IsAWindow(GenericPredicate):
    """
    Predicate subclass that looks for top-level windows.
    """


    def __init__(self):
        super().__init__(role_name="window")


class IsAWindowNamed(GenericPredicate):
    """
    Predicate subclass that looks for a top-level window by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="window")


class IsAFrameNamed(GenericPredicate):
    """
    Predicate subclass that looks for a top-level frame by name.
    """

    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name, role_name="frame")


class IsNamed(GenericPredicate):
    """
    Predicate subclass that looks simply by name.
    """
    def __init__(self, name=None):
        self.name = name

        if not self.name:
            LOGGER.info("You did not provide any 'name' to match.")
            self.name = "__invalid__"

        super().__init__(name=self.name)
