"""Utility functions for 'dumping' trees of Node objects.

Author: Zack Cerza <zcerza@redhat.com>"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

spacer = ' '
def plain (node, depth = 0):
    """
    Plain-text dump. The hierarchy is represented through indentation.
    The default indentation string is a single space, ' ', but can be changed.
    """
    print spacer*(depth) + str (node)
    try:
        for action in node.actions.values():
            print spacer*(depth + 1) + str (action)
    except AttributeError: pass
    try:
        for child in node.children:
            plain (child, depth + 1)
    except AttributeError: pass

