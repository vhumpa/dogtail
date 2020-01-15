# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from io import StringIO

"""
Utility functions for 'dumping' trees of Node objects.
"""

__author__ = """
Zack Cerza <zcerza@redhat.com>,
Matěj Cepl <mcepl@redhat.com>
"""

spacer = u" "

def dump_str(node):
    with StringIO as in_memory_stream:
        plain(node, output=in_memory_stream)
        stream_buffer = in_memory_stream.getvalue()
        return stream_buffer


def plain(node, output=None):
    """
    Plain-text dump. The hierarchy is represented through indentation.
    """

    stream_output = None
    close_output = False

    def crawl(node, depth):
        do_dump(node, depth)

        actions_keys = list(node.actions.keys())
        actions_keys.sort()

        for action in actions_keys:
            do_dump(node.actions[action], depth + 1)

        for child in node.children:
            crawl(child, depth + 1)


    def dumpFile(item, depth):
        stream_output.write(str(spacer * depth) + str(item) + str("\n"))


    def dumpStdOut(item, depth):
        try:
            print(spacer * depth + str(item))  # py3
        except UnicodeDecodeError:
            print(spacer * depth + str(item).decode("utf8"))  # py2 fallback

    do_dump = dumpFile if output else dumpStdOut

    if output:
        try:
            if hasattr(output, "write"):
                stream_output = output
            elif isinstance(output, basestring):  # py2
                stream_output = open(output, "w")
                close_output = True
        except NameError:
            if isinstance(output, str):  # there's no basestring in py3 (no str and unicode)
                stream_output = open(output, "w")
                close_output = True

    crawl(node, 0)

    if close_output:
        stream_output.close()


def verbose(node, output=None):
    """
    Verbose output is the same as plain but with attributes like
    position, size, visible, showing.
    Keeping output parameter for compatibility purpose.
    Always dumping to stdout
    """

    def crawl(node, depth):
        do_dump(node, depth)
        for child in node.children:
            crawl(child, depth + 1)

    def dump_std_out(item, depth):
        print(spacer * depth + str(item) + "     [p:%s, s:%s, vis:%s, show:%s]" % \
            item.position, item.size, item.visible, item.showing)

    do_dump = dump_std_out
    crawl(node, 0)
