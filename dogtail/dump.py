#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# ruff: noqa: E501

class AccessibleStructureRepresentation:
    """
    Accessible Structure Representation from given Accessible Node.
    """

    def __init__(self, accessible_node, structure_format="plain", file_name=None):
        self.spacer = "  "
        self.format = structure_format
        self.accessible_node = accessible_node
        self.tree_representation = ""
        self.file_name = file_name


    def _represent_structure_as_plain(self, acc_object, level=0):
        tree_representation = self.spacer * level + str(acc_object) + "\n"

        for child in acc_object.children:
            # Not adding Action strings by choice, we can revisit in the future.

            tree_representation += self._represent_structure_as_plain(child, level + 1)

        return tree_representation


    def _represent_structure_as_verbose(self, acc_object, level=0):
        if not acc_object:
            return

        verbose_str = "".join((
            str(acc_object),
            " - ",
            f"(position:'{acc_object.position}', size:'{acc_object.size}', ",
            f"visible:{acc_object.visible}, showing:{acc_object.showing})"
        ))

        tree_representation = self.spacer * level + verbose_str + "\n"

        for child in acc_object.children:
            # Not adding Action strings by choice, we can revisit in the future.

            tree_representation += self._represent_structure_as_verbose(child, level + 1)

        return tree_representation


    def _represent_structure_as_tree(self, node, last=True, spacer=""):
        self._recursive_tree_structure_construction(node, last=last, spacer=spacer)
        return self.tree_representation


    def _recursive_tree_structure_construction(self, node, last, spacer):
        if not node:
            return

        prefix_spacer = "    "
        prefix_extend = " │  "
        suffix_branch = " ├──"
        suffix_last =   " └──"

        # Attempt to shorten the line.
        suffix_based_on_last = suffix_last if last else suffix_branch
        # Add a line to the tree representation.
        self.tree_representation += (spacer + suffix_based_on_last + str(node))  + "\n"

        for index, child in enumerate(node.children):
            # Not adding Action strings by choice, we can revisit in the future.

            # Check if the index is last.
            is_last = index == node.child_count - 1
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
