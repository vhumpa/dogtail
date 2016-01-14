# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

"""
Utility functions for 'dumping' trees of Node objects.
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"


spacer = ' '


def plain(node, fileName=None):
    """
    Plain-text dump. The hierarchy is represented through indentation.
    """
    def crawl(node, depth):
        dump(node, depth)
        for action in list(node.actions.values()):
            dump(action, depth + 1)
        for child in node.children:
            crawl(child, depth + 1)

    def dumpFile(item, depth):
        _file.write(str(spacer * depth) + str(item) + str('\n'))

    def dumpStdOut(item, depth):
        try:
            print(spacer * depth + str(item))
        except UnicodeDecodeError:
            print(spacer * depth + str(item).decode('utf8'))

    if fileName:
        dump = dumpFile
        _file = open(fileName, 'w')
    else:
        dump = dumpStdOut

    crawl(node, 0)
