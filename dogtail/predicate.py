"""Predicates that can be used when searching for nodes.

Author: David Malcolm <dmalcolm@redhat.com>"""
__author__ = 'David Malcolm <dmalcolm@redhat.com>'

import unittest

from i18n import TranslatableString

def stringMatches(scriptName, reportedName):
    assert isinstance(scriptName, TranslatableString)

    return scriptName.matchedBy(reportedName)

def makeScriptRecursiveArgument(isRecursive, defaultValue):
    if isRecursive==defaultValue:
        return ""
    else:
        return ", recursive=%s"%isRecursive

def makeCamel(string):
    """
    Convert string to camelCaps
    """
    string = str(string)
    # FIXME: this function is probably really fragile, lots of difficult cases here

    # Sanitize string, replacing bad characters with spaces:
    for char in ":;!@#$%^&*()-+=_~`\\/?|[]{}<>,.\t\n\r\"'":
        string = string.replace(char, " ")
    words = string.strip().split(" ")
    for word in words:
        word.strip
    result = ""
    firstWord=True
    for word in words:
        lowercaseWord = word.lower()
        if firstWord:
            result += lowercaseWord
            firstWord=False
        else:
            result += lowercaseWord.capitalize()
    return result

class Predicate:
    """Abstract base class representing a predicate function on nodes.

    It's more than just a function in that it has data and can describe itself"""
    def satisfiedByNode(self, node):
        """Pure virtual method returning a boolean if the predicate is satisfied by the node"""
        raise NotImplementedError

    def describeSearchResult(self, node):
        raise NotImplementedError

    def makeScriptMethodCall(self, isRecursive):
        """
        Method to generate a string containing a (hopefully) readable search
        method call on a node (to be used when generating Python source code in
        the event recorder)
        """
        raise NotImplementedError

    def makeScriptVariableName(self):
        """
        Method to generate a string containing a (hopefully) readable name
        for a Node instance variable that would be the result of a search on
        this predicate (to be used when generating Python source code in the
        event recorder).
        """
        raise NotImplementedError

    def __eq__(self, other):
        """
        Predicates are considered equal if they are of the same subclass and
        have the same data
        """
        # print "predeq: self:%s"%self
        # print "               other:%s"%other
        # print "predeq: selfdict:%s"%self.__dict__
        # print "               otherdict:%s"%other.__dict__

        if type(self)!=type(other):
            return False
        else:
            return self.__dict__ == other.__dict__


class IsAnApplicationNamed(Predicate):
    """Search subclass that looks for an application by name"""
    def __init__(self, appName):
        self.appName = TranslatableString(appName)

    def satisfiedByNode(self, node):
        return node.roleName=='application' and stringMatches(self.appName, node.name)

    def describeSearchResult(self):
        return '%s application'%self.appName

    def makeScriptMethodCall(self, isRecursive):
        # ignores the isRecursive parameter
        return "application(%s)"%self.appName

    def makeScriptVariableName(self):
        return makeCamel(self.appName)+"App"

class GenericPredicate(Predicate):
    """SubtreePredicate subclass that takes various optional search fields"""

    def __init__(self, name = None, roleName = None, description= None, label = None, debugName=None):
        if name:
            self.name = TranslatableString(name)
        else:
            self.name = None
        self.roleName = roleName
        self.description = description
        if label:
            self.label = TranslatableString(label)
        else:
            self.label = None

        if debugName:
            self.debugName = debugName
        else:
            if label:
                self.debugName = "labelled '%s'"%self.label
            else:
                self.debugName = "child with"
            if name:
                self.debugName += " name=%s" % self.name
            if roleName:
                self.debugName += " roleName='%s'"%roleName
            if description:
                self.debugName += " description='%s'"%description
        assert self.debugName


    def satisfiedByNode(self, node):
        # labelled nodes are handled specially:
        if self.label:
            # this reverses the search; we're looking for a node with LABELLED_BY
            # and then checking the label, rather than looking for a label and
            # then returning whatever LABEL_FOR targets
            if node.labeller:
                return stringMatches(self.label, node.labeller.name)
            else: return False
        else:
            # Ensure the node matches any criteria that were set:
            if self.name:
                if not stringMatches(self.name,node.name): return False
            if self.roleName:
                if self.roleName!=node.roleName: return False
            if self.description:
                if self.description!=node.description: return False
            return True

    def describeSearchResult(self):
        return self.debugName

    def makeScriptMethodCall(self, isRecursive):
        if self.label:
            args = "label=%s"%label
        else:
            args = ""
            if self.name:
                args += " name=%s"%self.name
            if self.roleName:
                args += " roleName=%s"%self.roleName
            if self.description:
                args += " description=%s"%self.description
        return "child(%s%s)"%(args, makeScriptRecursiveArgument(isRecursive, True))

    def makeScriptVariableName(self):
        if self.label:
            return makeCamel(self.label)+"Node"
        else:
            if self.name:
                return makeCamel(self.name)+"Node"
            if self.roleName:
                return makeCamel(self.roleName)+"Node"
            if self.description:
                return makeCamel(self.description)+"Node"

class IsNamed(Predicate):
    """Predicate subclass that looks simply by name"""

    def __init__(self, name):
        self.name = TranslatableString(name)

    def satisfiedByNode(self, node):
        return stringMatches(self.name, node.name)

    def describeSearchResult(self):
        return "named %s"%self.name

    def makeScriptMethodCall(self, isRecursive):
        return "child(name=%s%s)"%(self.name, makeScriptRecursiveArgument(isRecursive, True))
    def makeScriptVariableName(self):
        return makeCamel(self.name)+"Node"

class IsAWindowNamed(Predicate):
    """Predicate subclass that looks for a top-level window by name"""
    def __init__(self, windowName):
        self.windowName = TranslatableString(windowName)

    def satisfiedByNode(self, node):
        return node.roleName=='frame' and stringMatches(self.windowName, node.name)

    def describeSearchResult(self):
        return "%s window"%self.windowName

    def makeScriptMethodCall(self, isRecursive):
        return "window(%s%s)"%(self.windowName, makeScriptRecursiveArgument(isRecursive, False))

    def makeScriptVariableName(self):
        return makeCamel(self.windowName)+"Win"

class IsAWindow(Predicate):
    """Predicate subclass that looks for top-level windows"""
    def satisfiedByNode(self, node):
        return node.roleName=='frame'

    def describeSearchResult(self):
        return "window"

class IsADialogNamed(Predicate):
    """Predicate subclass that looks for a top-level dialog by name"""
    def __init__(self, dialogName):
        self.dialogName = TranslatableString(dialogName)

    def satisfiedByNode(self, node):
        return node.roleName=='dialog' and stringMatches(self.dialogName, node.name)

    def describeSearchResult(self):
        return '%s dialog'%self.dialogName

    def makeScriptMethodCall(self, isRecursive):
        return "dialog(%s%s)"%(self.dialogName, makeScriptRecursiveArgument(isRecursive, False))

    def makeScriptVariableName(self):
        return makeCamel(self.dialogName)+"Dlg"

class IsLabelledBy(Predicate):
    """Predicate: is this node labelled by another node"""
    pass

class IsLabelledAs(Predicate):
    """Predicate: is this node labelled with the text string (i.e. by another node with that as a name)"""
    def __init__(self, labelText):
        self.labelText = TranslatableString(labelText)

    def satisfiedByNode(self, node):
        # FIXME
        if node.labeller:
            return stringMatches(self.labelText, node.labeller.name)
        else: return False

    def describeSearchResult(self):
        return 'labelled %s'%self.labelText

    def makeScriptMethodCall(self, isRecursive):
        return "child(label=%s%s)"%(self.labelText, makeScriptRecursiveArgument(isRecursive, True))

    def makeScriptVariableName(self):
        return makeCamel(self.labelText)+"Node"

class IsAMenuNamed(Predicate):
    """Predicate subclass that looks for a menu by name"""
    def __init__(self, menuName):
        self.menuName = TranslatableString(menuName)

    def satisfiedByNode(self, node):
        return node.roleName=='menu' and stringMatches(self.menuName, node.name)

    def describeSearchResult(self):
        return '%s menu'%(self.menuName)

    def makeScriptMethodCall(self, isRecursive):
        return "menu(%s%s)"%(self.menuName, makeScriptRecursiveArgument(isRecursive, True))

    def makeScriptVariableName(self):
        return makeCamel(self.menuName)+"Menu"

class IsAMenuItemNamed(Predicate):
    """Predicate subclass that looks for a menu item by name"""
    def __init__(self, menuItemName):
        self.menuItemName = TranslatableString(menuItemName)

    def satisfiedByNode(self, node):
        roleName = node.roleName
        return (roleName=='menu item' or roleName=='check menu item' or roleName=='radio menu item') and stringMatches(self.menuItemName, node.name)

    def describeSearchResult(self):
        return '%s menuitem'%(self.menuItemName)

    def makeScriptMethodCall(self, isRecursive):
        return "menuItem(%s%s)"%(self.menuItemName, makeScriptRecursiveArgument(isRecursive, True))

    def makeScriptVariableName(self):
        return makeCamel(self.menuItemName)+"MenuItem"

class IsATextEntryNamed(Predicate):
    """Predicate subclass that looks for a text entry by name"""
    def __init__(self, textEntryName):
        self.textEntryName = TranslatableString(textEntryName)

    def satisfiedByNode(self, node):
        return node.roleName=='text' and stringMatches(self.textEntryName, node.name)

    def describeSearchResult(self):
        return '%s textentry'%(self.textEntryName)

    def makeScriptMethodCall(self, isRecursive):
        return "textentry(%s%s)"%(self.textEntryName, makeScriptRecursiveArgument(isRecursive, True))

    def makeScriptVariableName(self):
        return makeCamel(self.textEntryName)+"Entry"

class IsAButtonNamed(Predicate):
    """Predicate subclass that looks for a button by name"""
    def __init__(self, buttonName):
        self.buttonName = TranslatableString(buttonName)

    def satisfiedByNode(self, node):
        return node.roleName=='push button' and stringMatches(self.buttonName, node.name)

    def describeSearchResult(self):
        return '%s button'%(self.buttonName)

    def makeScriptMethodCall(self, isRecursive):
        return "button(%s%s)"%(self.buttonName, makeScriptRecursiveArgument(isRecursive, True))

    def makeScriptVariableName(self):
        return makeCamel(self.buttonName)+"Button"

class IsATabNamed(Predicate):
    """Predicate subclass that looks for a tab by name"""
    def __init__(self, tabName):
        self.tabName = TranslatableString(tabName)

    def satisfiedByNode(self, node):
        return node.roleName=='page tab' and stringMatches(self.tabName, node.name)

    def describeSearchResult(self):
        return '%s tab'%(self.tabName)

    def makeScriptMethodCall(self, isRecursive):
        return "tab(%s%s)"%(self.tabName, makeScriptRecursiveArgument(isRecursive, True))

    def makeScriptVariableName(self):
        return makeCamel(self.tabName)+"Tab"

class PredicateTests(unittest.TestCase):
    def testCapitalization(self):
        self.assertEquals(makeCamel("gnome-terminal"),"gnomeTerminal")
        self.assertEquals(makeCamel("Evolution - Mail"), "evolutionMail")
        self.assertEquals(makeCamel('self.assertEquals(makeCamel("Evolution - Mail"), "evolutionMail")'), "selfAssertequalsMakecamelEvolutionMailEvolutionmail")

if __name__ == "__main__":
    unittest.main()
