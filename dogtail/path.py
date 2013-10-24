# -*- coding: utf-8 -*-
"""
Author: David Malcolm <dmalcolm@redhat.com>
"""
__author__ = """David Malcolm <dmalcolm@redhat.com>"""


class SearchPath(object):

    """
    Class used by the recording framework (and for more verbose script
    logging) for identifying nodes in a persistent way, independent of the
    style of script being written.

    Implemented as a list of (predicate, isRecursive) pairs, giving the
    'best' way to find the Accessible wrapped by a Node, starting at the
    root and applying each search in turn.

    This is somewhat analagous to an absolute path in a filesystem, except
    that some of searches may be recursive, rather than just searching
    direct children.

    FIXME: try to ensure uniqueness
    FIXME: need some heuristics to get 'good' searches, whatever
    that means
    """

    def __init__(self):
        self.__list = []

    def __str__(self):
        result = "{"
        for (predicate, isRecursive) in self.__list:
            result += "/(%s,%s)" % (
                predicate.describeSearchResult(), isRecursive)
        return result + "}"

    # We need equality to work so that dicts of these work:
    def __eq__(self, other):
        # print "eq: self:%s"%self
        # print "       other:%s"%other
        if len(self.__list) != len(other.__list):
            # print "nonequal length"
            return False
        else:
            for i in range(len(self.__list)):
                if self.__list[i] != other.__list[i]:
                    return False
        # print True
        return True

    def append(self, predicate, isRecursive):
        assert predicate
        self.__list.append((predicate, isRecursive))

    def __iter__(self):
        return iter(self.__list)

    def length(self):
        return len(self.__list)

    def makeScriptMethodCall(self):
        """
        Used by the recording system.

        Generate the Python source code that will carry out this search.
        """
        result = ""
        for (predicate, isRecursive) in self.__list:
            # print predicate
            # print self.generateVariableName(predicate)
            result += "." + predicate.makeScriptMethodCall(isRecursive)
        return result

    def getRelativePath(self, other):
        """
        Given another SearchPath instance, if the other is 'below' this
        one, return a SearchPath that describes how to reach it relative
        to this one (a copy of the second part of the list).    Otherwise
        return None.
        """
        for i in range(len(self.__list)):
            if self.__list[i] != other.__list[i]:
                break
        if i > 0:
            # Slice from this point to the end:
            result = SearchPath()
            result.__list = other.__list[i + 1:]

            if False:
                print("....................")
                print("from %s" % self)
                print("to %s" % other)
                print("i=%s" % i)
                print("relative path %s" % result)
                print("....................")

            return result
        else:
            return None

    def getPrefix(self, n):
        """
        Get the first n components of this instance as a new instance
        """
        result = SearchPath()
        for i in range(n):
            result.__list.append(self.__list[i])
        return result

    def getPredicate(self, i):
        (predicate, isRecursive) = self.__list[i]
        return predicate
