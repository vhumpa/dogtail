#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=line-too-long
# ruff: noqa: E501

class AccessibleStructureRepresentation:
    """
    Accessible Structure Representation from given Accessible Node.
    """

    # TODO - add with_labels and print x.labeler.name and x.labeler.text
    def __init__(self, accessible_node, structure_format="plain", file_name=None, labels=False):
        self.spacer = "  "
        self.format = structure_format
        self.accessible_node = accessible_node
        self.tree_representation = ""
        self.file_name = file_name
        self.labels = labels


    def _get_label_string(self, acc_object):
        labeler_string = ""
        if self.labels and acc_object.labeler:
            for iteration, labeler in enumerate(acc_object.labeler):
                labeler_string += f" (labeler_{iteration}.text='{labeler.text}') "
                labeler_string += f" (labeler_{iteration}.name='{labeler.name}') "

        if self.labels and not acc_object.labeler:
            labeler_string += " (No labeler) "

        return labeler_string


    def _represent_structure_as_plain(self, acc_object, level=0):
        labeler_string = self._get_label_string(acc_object)

        tree_representation = self.spacer * level + str(acc_object) + labeler_string + "\n"

        for child in acc_object.children:
            # Not adding Action strings by choice, we can revisit in the future.

            tree_representation += self._represent_structure_as_plain(child, level + 1)

        return tree_representation


    def _represent_structure_as_verbose(self, acc_object, level=0):
        if not acc_object:
            return

        labeler_string = self._get_label_string(acc_object)

        verbose_str = "".join((
            str(acc_object),
            " - ",
            f"(position:'{acc_object.position}', size:'{acc_object.size}', ",
            f"visible:{acc_object.visible}, showing:{acc_object.showing})",
            f"{labeler_string}"
        ))

        tree_representation = self.spacer * level + verbose_str + "\n"

        for child in acc_object.children:
            # Not adding Action strings by choice, we can revisit in the future.

            tree_representation += self._represent_structure_as_verbose(child, level + 1)

        return tree_representation


    def _represent_structure_as_tree(self, node, last=True, spacer=""):
        self._recursive_tree_structure_construction(node, last=last, spacer=spacer)
        return self.tree_representation


    def _recursive_tree_structure_construction(self, acc_object, last, spacer):
        if not acc_object:
            return

        prefix_spacer = "    "
        prefix_extend = " │  "
        suffix_branch = " ├──"
        suffix_last =   " └──"

        labeler_string = self._get_label_string(acc_object)

        # Attempt to shorten the line.
        suffix_based_on_last = suffix_last if last else suffix_branch
        # Add a line to the tree representation.

        self.tree_representation += (spacer + suffix_based_on_last + str(acc_object)) + labeler_string + "\n"

        for index, child in enumerate(acc_object.children):
            # Not adding Action strings by choice, we can revisit in the future.

            # Check if the index is last.
            is_last = index == acc_object.child_count - 1
            # Make a new spacer.
            new_spacer = spacer + (prefix_spacer if last else prefix_extend)

            self._recursive_tree_structure_construction(child, last=is_last, spacer=new_spacer)


    def load_data_to_file(self, data):
        """
        Insert Accessible Structure Representation to the file.

        :param data: Data to insert to the file.
        :type data: str

        :raises OSError: Raise OSError if the is an issue with file manipulation.
        """

        try:
            with open(self.file_name, "w", encoding="utf-8") as file_:
                file_.write(data)
        except OSError as error:
            raise OSError(f"Issue with opening '{self.file_name}' file.") from error


    def __str__(self):
        if self.format == "plain":
            plain_data = self._represent_structure_as_plain(self.accessible_node)

            if self.file_name:
                self.load_data_to_file(data=plain_data)
                return f"[ Plain structure was inserted in file '{self.file_name}'. ]"

            return plain_data

        if self.format == "verbose":
            verbose_data = self._represent_structure_as_verbose(self.accessible_node)

            if self.file_name:
                self.load_data_to_file(data=verbose_data)
                return f"[ Verbose structure was inserted in file '{self.file_name}'. ]"

            return verbose_data

        if self.format == "tree":
            tree_data = self._represent_structure_as_tree(self.accessible_node)

            if self.file_name:
                self.load_data_to_file(data=tree_data)
                return f"[ Tree structure was inserted in file '{self.file_name}'. ]"

            return tree_data

        return f"[Unknown format selected '{self.format}']"


    def __repr__(self):
        return "<Accessible Structure Representation>"
