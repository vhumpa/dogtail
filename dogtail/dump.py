"""Utility functions for 'dumping' trees of Node objects.

Author: Zack Cerza <zcerza@redhat.com>"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

from __builtin__ import file

spacer = ' '


def plain(node, fileName=None):
    """
    Plain-text dump. The hierarchy is represented through indentation.
    """
    def crawl(node, depth):
        dump(node, depth)
        for action in node.actions.values():
            dump(action, depth + 1)
        for child in node.children:
            crawl(child, depth + 1)

    def dumpFile(item, depth):
        _file.write(spacer * depth + str(item) + '\n')

    def dumpStdOut(item, depth):
        print(spacer * depth + str(item))
    if fileName:
        dump = dumpFile
        _file = file(fileName, 'w')
    else:
        dump = dumpStdOut

    crawl(node, 0)
