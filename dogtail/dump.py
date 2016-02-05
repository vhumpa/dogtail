# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
"""Utility functions for 'dumping' trees of Node objects.

Author: Zack Cerza <zcerza@redhat.com>, Matěj Cepl <mcepl@redhat.com>"""
from io import StringIO

spacer = u' '


def dump_str(node):
    with StringIO as tmp_file:
        plain(node, output=tmp_file)
        dump_str = tmp_file.getvalue()
        return dump_str


def plain(node, output=None):
    """
    Plain-text dump. The hierarchy is represented through indentation.
    """
    close_output = False

    def crawl(node, depth):
        do_dump(node, depth)
        for action in node.actions.values():
            do_dump(action, depth + 1)
        for child in node.children:
            crawl(child, depth + 1)

    def node2unicode(node):
        return str(node).decode('utf8')

    def dumpFile(item, depth):
        _file.write(spacer * depth + node2unicode(item) + u'\n')

    def dumpStdOut(item, depth):
        print(spacer * depth + node2unicode(item))

    _file = None

    if output:
        do_dump = dumpFile
        if hasattr(output, 'write'):
            _file = output
        elif isinstance(output, basestring):
            _file = open(output, 'w')
            close_output = True
    else:
        do_dump = dumpStdOut

    crawl(node, 0)

    if close_output:
        _file.close()
