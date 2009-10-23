"""Makes some sense of the AT-SPI API

The tree API handles various things for you:
    - fixes most timing issues
    - can automatically generate (hopefully) highly-readable logs of what the
script is doing
    - traps various UI malfunctions, raising exceptions for them (again,
hopefully improving the logs)

The most important class is Node. Each Node is an element of the desktop UI.
There is a tree of nodes, starting at 'root', with applications as its
children, with the top-level windows and dialogs as their children. The various
widgets that make up the UI appear as descendents in this tree. All of these
elements (root, the applications, the windows, and the widgets) are represented
as instances of Node in a tree (provided that the program of interest is
correctly exporting its user-interface to the accessibility system). The Node
class is a mixin for Accessible and the various Accessible interfaces.

The Action class represents an action that the accessibility layer exports as
performable on a specific node, such as clicking on it. It's a wrapper around
Accessibility.Action.

We often want to look for a node, based on some criteria, and this is provided
by the Predicate class.

Dogtail implements a high-level searching system, for finding a node (or
nodes) satisfying whatever criteria you are interested in. It does this with
a 'backoff and retry' algorithm. This fixes most timing problems e.g. when a
dialog is in the process of opening but hasn't yet done so.

If a search fails, it waits 'config.searchBackoffDuration' seconds, and then
tries again, repeatedly. After several failed attempts (determined by
config.searchWarningThreshold) it will start sending warnings about the search
to the debug log. If it still can't succeed after 'config.searchCutoffCount'
attempts, it raises an exception containing details of the search. You can see
all of this process in the debug log by setting 'config.debugSearching' to True

We also automatically add a short delay after each action
('config.defaultDelay' gives the time in seconds). We'd hoped that the search
backoff and retry code would eliminate the need for this, but unfortunately we
still run into timing issues. For example, Evolution (and probably most
other apps) set things up on new dialogs and wizard pages as they appear, and
we can run into 'setting wars' where the app resets the widgetry to defaults
after our script has already filled out the desired values, and so we lose our
values. So we give the app time to set the widgetry up before the rest of the
script runs.

The classes trap various UI malfunctions and raise exceptions that better
describe what went wrong. For example, they detects attempts to click on an
insensitive UI element and raise a specific exception for this.

Unfortunately, some applications do not set up the 'sensitive' state
correctly on their buttons (e.g. Epiphany on form buttons in a web page). The
current workaround for this is to set config.ensureSensitivity=False, which
disables the sensitivity testing.

Authors: Zack Cerza <zcerza@redhat.com>, David Malcolm <dmalcolm@redhat.com>
"""
__author__ = """Zack Cerza <zcerza@redhat.com>,
David Malcolm <dmalcolm@redhat.com>
"""

from config import config
if config.checkForA11y:
    from utils import checkForA11y
    checkForA11y()

import re
import predicate
from datetime import datetime
from time import sleep
from utils import doDelay
from utils import Blinker
import rawinput
import path

from logging import debugLogger as logger

try:
    import pyatspi
    import Accessibility
except ImportError:
    raise ImportError, "Error importing the AT-SPI bindings"

from CORBA import COMM_FAILURE, OBJECT_NOT_EXIST

# We optionally import the bindings for libwnck.
try:
    import wnck
    gotWnck = True
except ImportError:
    # Skip this warning, since the functionality is almost entirely nonworking anyway.
    #print "Warning: Dogtail could not import the Python bindings for libwnck. Window-manager manipulation will not be available."
    gotWnck = False

haveWarnedAboutChildrenLimit = False

class SearchError(Exception):
    pass

class NotSensitiveError(Exception):
    """
    The widget is not sensitive.
    """
    message = "Cannot %s %s. It is not sensitive."
    def __init__(self, action):
        self.action = action

    def __str__(self):
        return self.message % (self.action.name, self.action.node.getLogString())

class ActionNotSupported(Exception):
    """
    The widget does not support the requested action.
    """
    message = "Cannot do '%s' action on %s"
    def __init__(self, actionName, node):
        self.actionName = actionName
        self.node = node

    def __str__(self):
        return self.message % (self.actionName, self.node.getLogString())

class Action:
    """
    Class representing an action that can be performed on a specific node
    """
    # Valid types of actions we know about. Feel free to add any you see.
    types = ('click',
             'press',
             'release',
             'activate',
             'jump',
             'check',
             'dock',
             'undock',
             'open',
             'menu')

    def __init__ (self, node, action, index):
        self.node = node
        self.__action = action
        self.__index = index

    def _getName(self): return self.__action.getName(self.__index)
    name = property(_getName)

    def _getDescription(self): return self.__action.getDescription(self.__index)
    description = property(_getDescription)

    def _getKeyBinding(self): return self.__action.getKeyBinding(self.__index)
    keyBinding = property(_getKeyBinding)

    def __str__ (self):
        return "[action | %s | %s ]" % \
            (self.name, self.keyBinding)

    def do (self):
        """
        Performs the given tree.Action, with appropriate delays and logging.
        """
        logger.log("%s on %s"%(self.name, self.node.getLogString()))
        if not self.node.sensitive:
            if config.ensureSensitivity:
                raise NotSensitiveError, self
            else:
                nSE = NotSensitiveError(self)
                logger.log("Warning: " + str(nSE))
        if config.blinkOnActions: self.node.blink()
        result = self.__action.doAction (self.__index)
        doDelay(config.actionDelay)
        return result
        

class Node:
    """
    A node in the tree of UI elements. This class is mixed in with 
    Accessibility.Accessible to both make it easier to use and to add 
    additional functionality. It also has a debugName which is set up 
    automatically when doing searches.
    """

    def __setupUserData(self):
        try: len(self.user_data)
        except (AttributeError, TypeError): self.user_data = {}

    def _getDebugName(self):
        self.__setupUserData()
        return self.user_data.get('debugName', None)

    def _setDebugName(self, debugName):
        self.__setupUserData()
        self.user_data['debugName'] = debugName

    debugName = property(_getDebugName, _setDebugName, doc = \
            "debug name assigned during search operations")

    ##
    # Accessible
    ##
    def _getDead(self):
        try:
            if self.roleName == 'invalid': return True
            n = self.role
            n = self.name
            if len(self) > 0: n = self[0]
        except (LookupError, COMM_FAILURE, OBJECT_NOT_EXIST): return True
        return False
    dead = property(_getDead, doc = "Is the node dead (defunct) ?")

    def _getChildren(self):
        if self.parent and self.parent.roleName == 'hyper link':
            print self.parent.role
            return []
        children = []
        childCount = self.childCount
        if childCount > config.childrenLimit:
            global haveWarnedAboutChildrenLimit
            if not haveWarnedAboutChildrenLimit:
                logger.log("Only returning %s children. You may change config.childrenLimit if you wish. This message will only be printed once." % str(config.childrenLimit))
                haveWarnedAboutChildrenLimit = True
                childCount = config.childrenLimit
        for i in range(childCount):
            # Workaround for GNOME bug #465103
            # also solution for GNOME bug #321273
            try:
                child = self[i]
            except LookupError: child = None
            if child: children.append(child)

        invalidChildren = childCount - len(children)
        if invalidChildren and config.debugSearching:
            logger.log("Skipped %s invalid children of %s" % \
                    (invalidChildren, str(self)))
        try:
            ht = self.queryHypertext()
            for li in range(ht.getNLinks()):
                link = ht.getLink(li)
                for ai in range(link.nAnchors):
                    child = link.getObject(ai)
                    child.__setupUserData()
                    child.user_data['linkAnchor'] = \
                            LinkAnchor(node = child, \
                                        hypertext = ht, \
                                        linkIndex = li, \
                                        anchorIndex = ai )
                    children.append(child)
        except NotImplementedError: pass

        return children
    children = property(_getChildren, doc = \
        "a list of this Accessible's children")
    roleName = property(Accessibility.Accessible.getRoleName)
    role = property(Accessibility.Accessible.getRole)

    indexInParent = property(Accessibility.Accessible.getIndexInParent)

    ##
    # Action
    ##

    def doAction(self, name):
        """
        Perform the action with the specified name. For a list of actions
        supported by this instance, check the 'actions' property.
        """
        actions = self.actions
        if actions.has_key(name):
            return actions[name].do()
        raise ActionNotSupported(name, self)

    def _getActions(self):
        actions = {}
        try:
            action = self.queryAction()
            for i in range(action.nActions):
                a = Action(self, action, i)
                actions[action.getName(i)] = a
        finally:
            return actions
    actions = property(_getActions, doc = \
    """
    A dictionary of supported action names as keys, with Action objects as 
    values. Common action names include:
    
    'click' 'press' 'release' 'activate' 'jump' 'check' 'dock' 'undock'
    'open' 'menu'
    """)


    def _getComboValue(self): return self.name
    def _setComboValue(self, value):
        logger.log("Setting combobox %s to '%s'"%(self.getLogString(), value))
        self.childNamed(childName=value).doAction('click')
        doDelay()
    combovalue = property(_getComboValue, _setComboValue, doc = \
        """The value (as a string) currently selected in the combo box.""")

    ##
    # Hypertext and Hyperlink
    ##

    def _getURI(self):
        try: return self.user_data['linkAnchor'].URI
        except (KeyError, AttributeError): raise NotImplementedError
    URI = property(_getURI)


    ##
    # Text and EditableText
    ##

    def _getText(self):
        try: return self.queryText().getText(0,-1)
        except NotImplementedError: return None
    def _setText(self, text):
         try:
             if config.debugSearching:
                 msg = "Setting text of %s to %s"
                 # Let's not get too crazy if 'text' is really large...
                 # FIXME: Sometimes the next line screws up Unicode strings.
                 if len(text) > 140: txt = text[:134] + " [...]"
                 else: txt = text
                 logger.log(msg % (self.getLogString(), "'%s'" % txt)) 
             self.queryEditableText().setTextContents(text)
         except NotImplementedError: raise AttributeError, "can't set attribute"
    text = property(_getText, _setText, doc = \
        """For instances with an AccessibleText interface, the text as a 
        string. This is read-only, unless the instance also has an 
        AccessibleEditableText interface. In this case, you can write values 
        to the attribute. This will get logged in the debug log, and a delay 
        will be added.
    
        If this instance corresponds to a password entry, use the passwordText 
        property instead.""")

    def _getCaretOffset(self): return self.queryText().caretOffset
    def _setCaretOffset(self, offset):
        return self.queryText().setCaretOffset(offset)
    caretOffset = property(_getCaretOffset, _setCaretOffset, doc = \
         """For instances with an AccessibleText interface, the caret offset 
         as an integer.""")


    ##
    # Component
    ##

    def _getPosition(self):
        return self.queryComponent().getPosition(pyatspi.DESKTOP_COORDS)
    position = property(_getPosition, doc = \
        """A tuple containing the position of the Accessible: (x, y)""")

    def _getSize(self): return self.queryComponent().getSize()
    size = property(_getSize, doc = \
        """A tuple containing the size of the Accessible: (w, h)""")

    def _getExtents(self):
        try:
            ex = self.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            return (ex.x, ex.y, ex.width, ex.height)
        except NotImplementedError: return None
    extents = property(_getExtents, doc = \
        """
        A tuple containing the location and size of the Accessible: (x, y, w, h)
        """)

    def contains(self, x, y):
        try: return self.queryComponent().contains(x, y, pyatspi.DESKTOP_COORDS)
        except NotImplementedError: return False

    def getChildAtPoint(self, x, y):
        node = self
        while True:
            try:
                child = node.queryComponent().getAccessibleAtPoint(x, y,
                        pyatspi.DESKTOP_COORDS)
                if child and child.contains(x, y): node = child
                else: break
            except NotImplementedError: break
        if node and node.contains(x, y): return node
        else: return None

    def grabFocus(self):
        "Attempts to set the keyboard focus to this Accessible."
        return self.queryComponent().grabFocus()

    def blink(self, count=2):
        """
        Blink, baby!
        """
        if not self.extents: return False
        else: 
            (x, y, w, h) = self.extents
            from utils import Blinker
            blinkData = Blinker(x, y, w, h, count)
            return True

    def click(self, button = 1):
        """
        Generates a raw mouse click event, using the specified button.
            - 1 is left,
            - 2 is middle,
            - 3 is right.
        """
        clickX = self.position[0] + self.size[0]/2
        clickY = self.position[1] + self.size[1]/2
        if config.debugSearching:
            logger.log("raw click on %s %s at (%s,%s)"%(self.name, self.getLogString(), str(clickX), str(clickY)))
        rawinput.click(clickX, clickY, button)

    def doubleClick(self, button = 1):
        """
        Generates a raw mouse double-click event, using the specified button.
        """
        clickX = self.position[0] + self.size[0]/2
        clickY = self.position[1] + self.size[1]/2
        if config.debugSearching:
            logger.log("raw click on %s %s at (%s,%s)"%(self.name, self.getLogString(), str(clickX), str(clickY)))
        rawinput.doubleClick(clickX, clickY, button)


    ##
    # RelationSet
    ##
    def _labeler(self):
        relationSet = self.getRelationSet()
        for relation in relationSet:
            if relation.getRelationType() == pyatspi.RELATION_LABELLED_BY:
                    if relation.getNTargets() == 1: 
                        return relation.getTarget(0)
                    targets = []
                    for i in range(relation.getNTargets()):
                        targets.append(relation.getTarget(i))
                    return targets
    labeler = property(_labeler, doc = \
        """
        'labeller' (read-only list of Node instances):
        The node(s) that is/are a label for this node. Generated from
        'relations'.
        """)
    labeller = property(_labeler, doc = "See labeler")

    def _labelee(self):
        relationSet = self.getRelationSet()
        for relation in relationSet:
            if relation.getRelationType() == pyatspi.RELATION_LABEL_FOR:
                    if relation.getNTargets() == 1: 
                        return relation.getTarget(0)
                    targets = []
                    for i in range(relation.getNTargets()):
                        targets.append(relation.getTarget(i))
                    return targets
    labelee = property(_labelee, doc = \
        """
        'labellee' (read-only list of Node instances):
        The node(s) that this node is a label for. Generated from 'relations'.
        """)
    labellee = property(_labelee, doc = "See labelee")

    ##
    # StateSet
    ##
    def _isSensitive(self): return self.getState().contains(pyatspi.STATE_SENSITIVE)
    sensitive = property(_isSensitive, doc = \
        "Is the Accessible sensitive (i.e. not greyed out)?")

    def _isShowing(self): return self.getState().contains(pyatspi.STATE_SHOWING)
    showing = property(_isShowing)

    def _isFocusable(self): return self.getState().contains(pyatspi.STATE_FOCUSABLE)
    focusable = property(_isFocusable, doc = \
        "Is the Accessible capable of having keyboard focus?")

    def _isFocused(self): return self.getState().contains(pyatspi.STATE_FOCUSED)
    focused = property(_isFocused, doc = \
        "Does the Accessible have keyboard focus?")

    def _isChecked(self): return self.getState().contains(pyatspi.STATE_CHECKED)
    checked = property(_isChecked, doc = \
        "Is the Accessible a checked checkbox?")

    ##
    # Selection
    ##

    def selectAll(self):
        """
        Selects all children.
        """
        result = self.querySelection().selectAll()
        doDelay()
        return result

    def deselectAll(self):
        """
        Deselects all selected children.
        """
        result = self.querySelection().clearSelection()
        doDelay()
        return result

    def select(self):
        """
        Selects the Accessible.
        """
        try: parent = self.parent
        except AttributeError: raise NotImplementedError
        result = parent.querySelection().selectChild(self.indexInParent)
        doDelay()
        return result

    def deselect(self):
        """
        Deselects the Accessible.
        """
        try: parent = self.parent
        except AttributeError: raise NotImplementedError
        result = parent.querySelection().deselectChild(self.indexInParent)
        doDelay()
        return result
    
    def _getSelected(self):
        try: parent = self.parent
        except AttributeError: raise NotImplementedError
        return parent.querySelection().isChildSelected(self.indexInParent)
    isSelected = property(_getSelected, doc = "Is the Accessible selected?")
    
    def _getSelectedChildren(self):
        #TODO: hideChildren for Hyperlinks?
        selection = self.querySelection()
        selectedChildren = []
        for i in xrange(selection.nSelectedChildren):
            selectedChildren.append(selection.getSelectedChild(i))
    selectedChildren = property(_getSelectedChildren, doc = \
        "Returns a list of children that are selected.")

    ##
    # Value
    ##

    @property
    def value(self):
        try: return self.queryValue().currentValue
        except NotImplementedError: pass

    @value.setter
    def value(self, value):
        self.queryValue().currentValue = value

    @property
    def minValue(self):
        try: return self.queryValue().minimumValue
        except NotImplementedError: pass

    @property
    def minValueIncrement(self):
        try: return self.queryValue().minimumIncrement
        except NotImplementedError: pass

    @property
    def maxValue(self):
        try: return self.queryValue().maximumValue
        except NotImplementedError: pass

    def typeText(self, string):
        """
        Type the given text into the node, with appropriate delays and
        logging.
        """
        logger.log("Typing text into %s: '%s'"%(self.getLogString(), string))

        if self.focusable:
            if not self.focused:
                try: self.grabFocus()
                except Exception: logger.log("Node is focusable but I can't grabFocus!")
            rawinput.typeText(string)
        else:
            logger.log("Node is not focusable; falling back to inserting text")
            et = self.queryEditableText()
            et.insertText(self.caretOffset, string, len(string))
            self.caretOffset += len(string)
            doDelay()

    def keyCombo(self, comboString):
        if config.debugSearching: logger.log("Pressing keys '%s' into %s"%(combo, self.getLogString()))
        if self.focusable:
            if not self.focused:
                try: self.grabFocus()
                except Exception: logger.log("Node is focusable but I can't grabFocus!")
        else: logger.log("Node is not focusable; trying key combo anyway")
        rawinput.keyCombo(comboString)


    def getLogString(self):
        """
        Get a string describing this node for the logs,
        respecting the config.absoluteNodePaths boolean.
        """
        if config.absoluteNodePaths:
            return self.getAbsoluteSearchPath()
        else:
            return str(self)

    def satisfies (self, pred):
        """
        Does this node satisfy the given predicate?
        """
        # the logic is handled by the predicate:
        assert isinstance(pred, predicate.Predicate)
        return pred.satisfiedByNode(self)

    def dump (self, type = 'plain', fileName = None):
        import dump
        dumper = getattr (dump, type)
        dumper (self, fileName)

    def getAbsoluteSearchPath(self):
        """
        FIXME: this needs rewriting...
        Generate a SearchPath instance giving the 'best'
        way to find the Accessible wrapped by this node again, starting
        at the root and applying each search in turn.

        This is somewhat analagous to an absolute path in a filesystem,
        except that some of searches may be recursive, rather than just
        searching direct children.

        Used by the recording framework for identifying nodes in a
        persistent way, independent of the style of script being
        written.

        FIXME: try to ensure uniqueness
        FIXME: need some heuristics to get 'good' searches, whatever
        that means
        """
        if config.debugSearchPaths:
            logger.log("getAbsoluteSearchPath(%s)" % self)

        if self.roleName=='application':
            result =path.SearchPath()
            result.append(predicate.IsAnApplicationNamed(self.name), False)
            return result
        else:
            if self.parent:
                (ancestor, pred, isRecursive) = self.getRelativeSearch()
                if config.debugSearchPaths:
                    logger.log("got ancestor: %s" % ancestor)

                ancestorPath = ancestor.getAbsoluteSearchPath()
                ancestorPath.append(pred, isRecursive)
                return ancestorPath
            else:
                # This should be the root node:
                return path.SearchPath()

    def getRelativeSearch(self):
        """
        Get a (ancestorNode, predicate, isRecursive) triple that identifies the
        best way to find this Node uniquely.
        FIXME: or None if no such search exists?
        FIXME: may need to make this more robust
        FIXME: should this be private?
        """
        if config.debugSearchPaths:
            logger.log("getRelativeSearchPath(%s)" % self)

        assert self
        assert self.parent

        isRecursive = False
        ancestor = self.parent

        # iterate up ancestors until you reach an identifiable one,
        # setting the search to be isRecursive if need be:
        while not self.__nodeIsIdentifiable(ancestor):
            ancestor = ancestor.parent
            isRecursive = True

        # Pick the most appropriate predicate for finding this node:
        if self.labellee:
            if self.labellee.name:
                return (ancestor, predicate.IsLabelledAs(self.labellee.name), isRecursive)

        if self.roleName=='menu':
            return (ancestor, predicate.IsAMenuNamed(self.name), isRecursive)
        elif self.roleName=='menu item' or self.roleName=='check menu item':
            return (ancestor, predicate.IsAMenuItemNamed(self.name), isRecursive)
        elif self.roleName=='text':
            return (ancestor, predicate.IsATextEntryNamed(self.name), isRecursive)
        elif self.roleName=='push button':
            return (ancestor, predicate.IsAButtonNamed(self.name), isRecursive)
        elif self.roleName=='frame':
            return (ancestor, predicate.IsAWindowNamed(self.name), isRecursive)
        elif self.roleName=='dialog':
            return (ancestor, predicate.IsADialogNamed(self.name), isRecursive)
        else:
            pred = predicate.GenericPredicate(name=self.name, roleName=self.roleName)
            return (ancestor, pred, isRecursive)

    def __nodeIsIdentifiable(self, ancestor):
        if ancestor.labellee:
            return True
        elif ancestor.name:
            return True
        elif not ancestor.parent:
            return True
        else:
            return False

    def _fastFindChild(self, pred, recursive = True):
        """
        Searches for an Accessible using methods from pyatspi.utils
        """
        if isinstance(pred, predicate.Predicate): pred = pred.satisfiedByNode
        if not recursive:
            cIter = iter(self)
            while True:
                try: child = cIter.next()
                except StopIteration: break
                if child is not None: 
                    if pred(child): return child
        else: return pyatspi.utils.findDescendant(self, pred)

    def findChild(self, pred, recursive = True, debugName = None, \
            retry = True, requireResult = True):
        """
        Search for a node satisyfing the predicate, returning a Node.

        If retry is True (the default), it makes multiple attempts,
        backing off and retrying on failure, and eventually raises a
        descriptive exception if the search fails.

        If retry is False, it gives up after one attempt.

        If requireResult is True (the default), an exception is raised after all
        attempts have failed. If it is false, the function simply returns None.
        """
        def describeSearch (parent, pred, recursive, debugName):
            """
            Internal helper function
            """
            if recursive: noun = "descendent"
            else: noun = "child"
            if debugName == None: debugName = pred.describeSearchResult()
            return "%s of %s: %s"%(noun, parent.getLogString(), debugName)

        assert isinstance(pred, predicate.Predicate)
        numAttempts = 0
        while numAttempts < config.searchCutoffCount:
            if numAttempts >= config.searchWarningThreshold or config.debugSearching:
                logger.log("searching for %s (attempt %i)" % \
                        (describeSearch(self, pred, recursive, debugName), numAttempts))

            result = self._fastFindChild(pred.satisfiedByNode, recursive)
            if result:
                assert isinstance(result, Node)
                if debugName: result.debugName = debugName
                else: result.debugName = pred.describeSearchResult()
                return result
            else:
                if not retry: break
                numAttempts += 1
                if config.debugSearching or config.debugSleep:
                    logger.log("sleeping for %f" % config.searchBackoffDuration)
                sleep(config.searchBackoffDuration)
        if requireResult:
            raise SearchError(describeSearch(self, pred, recursive, debugName))

    # The canonical "search for multiple" method:
    def findChildren(self, pred, recursive = True):
        """
        Find all children/descendents satisfying the predicate.
        """
        if isinstance(pred, predicate.Predicate): pred = pred.satisfiedByNode
        if not recursive:
            cIter = iter(self)
            result = []
            while True:
                try: child = cIter.next()
                except StopIteration: break
                if child is not None and pred(child): result.append(child)
            return result
        else: return pyatspi.utils.findAllDescendants(self, pred)

    # The canonical "search above this node" method:
    def findAncestor (self, pred):
        """
        Search up the ancestry of this node, returning the first Node
        satisfying the predicate, or None.
        """
        assert isinstance(pred, predicate.Predicate)
        candidate = self.parent
        while candidate != None:
            if candidate.satisfies(pred):
                return candidate
            else:
                candidate = candidate.parent
        # Not found:
        return None


    # Various wrapper/helper search methods:
    def child (self, name = '', roleName = '', description= '', label = '', recursive=True, debugName=None):
        """
        Finds a child satisying the given criteria.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return self.findChild (predicate.GenericPredicate(name = name, roleName = roleName, description= description, label = label), recursive = recursive, debugName=debugName)

    def menu(self, menuName, recursive=True):
        """
        Search below this node for a menu with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return self.findChild (predicate.IsAMenuNamed(menuName=menuName), recursive)

    def menuItem(self, menuItemName, recursive=True):
        """
        Search below this node for a menu item with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return self.findChild (predicate.IsAMenuItemNamed(menuItemName=menuItemName), recursive)

    def textentry(self, textEntryName, recursive=True):
        """
        Search below this node for a text entry with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return self.findChild (predicate.IsATextEntryNamed(textEntryName=textEntryName), recursive)

    def button(self, buttonName, recursive=True):
        """
        Search below this node for a button with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return self.findChild (predicate.IsAButtonNamed(buttonName=buttonName), recursive)

    def childLabelled(self, labelText, recursive=True):
        """
        Search below this node for a child labelled with the given text.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return self.findChild (predicate.IsLabelledAs(labelText), recursive)

    def childNamed(self, childName, recursive=True):
        """
        Search below this node for a child with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return self.findChild (predicate.IsNamed(childName), recursive)

    def tab(self, tabName, recursive=True):
        """
        Search below this node for a tab with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return self.findChild (predicate.IsATabNamed(tabName=tabName), recursive)

    def getUserVisibleStrings(self):
        """
        Get all user-visible strings in this node and its descendents.

        (Could be implemented as an attribute)
        """
        result=[]
        if self.name:
            result.append(self.name)
        if self.description:
            result.append(self.description)
        try:
            children = self.children
        except Exception: return result
        for child in children:
            result.extend(child.getUserVisibleStrings())
        return result

    def blink(self, count = 2):
        """
        Blink, baby!
        """
        if not self.extents:
            return False
        else:
            (x, y, w, h) = self.extents
            blinkData = Blinker(x, y, w, h, count)
            return True


class LinkAnchor:
    """
    Class storing info about an anchor within an Accessibility.Hyperlink, which
    is in turn stored within an Accessibility.Hypertext.
    """

    def __init__(self, node, hypertext, linkIndex, anchorIndex):
        self.node = node
        self.hypertext = hypertext
        self.linkIndex = linkIndex
        self.anchorIndex = anchorIndex

    def _getLink(self):
        return self.hypertext.getLink(self.linkIndex)
    link = property(_getLink)

    def _getURI(self):
        return self.link.getURI(self.anchorIndex)
    URI = property(_getURI)


class Root (Node):
    """
    FIXME:
    """
    def applications(self):
        """
        Get all applications.
        """
        return root.findChildren(predicate.GenericPredicate( \
                roleName="application"), recursive=False)

    def application(self, appName):
        """
        Gets an application by name, returning an Application instance
        or raising an exception.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return root.findChild(predicate.IsAnApplicationNamed(appName),recursive=False)

class Application (Node):
    def dialog(self, dialogName, recursive=False):
        """
        Search below this node for a dialog with the given name,
        returning a Window instance.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.

        FIXME: should this method activate the dialog?
        """
        return self.findChild(predicate.IsADialogNamed(dialogName=dialogName), recursive)

    def window(self, windowName, recursive=False):
        """
        Search below this node for a window with the given name,
        returning a Window instance.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.

        FIXME: this bit isn't true:
        The window will be automatically activated (raised and focused
        by the window manager) if wnck bindings are available.
        """
        result = self.findChild (predicate.IsAWindowNamed(windowName=windowName), recursive)
        # FIXME: activate the WnckWindow ?
        #if gotWnck:
        #       result.activate()
        return result

    def getWnckApplication(self):
        """
        Get the wnck.Application instance for this application, or None

        Currently implemented via a hack: requires the app to have a
        window, and looks up the application of that window

        wnck.Application can give you the pid, the icon, etc

        FIXME: untested
        """
        window = child(roleName='frame')
        if window:
            wnckWindow = window.getWnckWindow()
            return wnckWindow.get_application()



class Window (Node):
    def getWnckWindow(self):
        """
        Get the wnck.Window instance for this window, or None
        """
        # FIXME: this probably needs rewriting:
        screen = wnck.screen_get_default()

        # You have to force an update before any of the wnck methods
        # do anything:
        screen.force_update()

        for wnckWindow in screen.get_windows():
            # FIXME: a dubious hack: search by window title:
            if wnckWindow.get_name()==self.name:
                return wnckWindow

    def activate(self):
        """
        Activates the wnck.Window associated with this Window.

        FIXME: doesn't yet work
        """
        wnckWindow = self.getWnckWindow()
        # Activate it with a timestamp of 0; this may confuse
        # alt-tabbing through windows etc:
        # FIXME: is there a better way of getting a timestamp?
        # gdk_x11_get_server_time (), with a dummy window
        wnckWindow.activate(0)

class Wizard (Window):
    """
    Note that the buttons of a GnomeDruid were not accessible until
    recent versions of libgnomeui.  This is
    http://bugzilla.gnome.org/show_bug.cgi?id=157936
    and is fixed in gnome-2.10 and gnome-2.12 (in CVS libgnomeui);
    there's a patch attached to that bug.

    This bug is known to affect FC3; fixed in FC5
    """
    def __init__(self, node, debugName=None):
        Node.__init__(self, node)
        if debugName:
            self.debugName = debugName
        logger.log("%s is on '%s' page"%(self, self.getPageTitle()))

    def currentPage(self):
        """
        Get the current page of this wizard

        FIXME: this is currently a hack, supporting only GnomeDruid
        """
        pageHolder = self.child(roleName='panel')
        for child in pageHolder.children:
            # current child has SHOWING state set, we hope:
            #print child
            #print child.showing
            if child.showing:
                return child
        raise "Unable to determine current page of %s"%self

    def getPageTitle(self):
        """
        Get the string title of the current page of this wizard

        FIXME: this is currently a total hack, supporting only GnomeDruid
        """
        currentPage = self.currentPage()
        return currentPage.child(roleName='panel').child(roleName='panel').child(roleName='label', recursive=False).text

    def clickForward(self):
        """
        Click on the 'Forward' button to advance to next page of wizard.

        It will log the title of the new page that is reached.

        FIXME: what if it's Next rather than Forward ???

        This will only work if your libgnomeui has accessible buttons;
        see above.
        """
        fwd = self.child("Forward")
        fwd.click()

        # Log the new wizard page; it's helpful when debugging scripts
        logger.log("%s is now on '%s' page"%(self, self.getPageTitle()))
        # FIXME disabled for now (can't get valid page titles)

    def clickApply(self):
        """
        Click on the 'Apply' button to advance to next page of wizard.
        FIXME: what if it's Finish rather than Apply ???

        This will only work if your libgnomeui has accessible buttons;
        see above.
        """
        fwd = self.child("Apply")
        fwd.click()

        # FIXME: debug logging?

Accessibility.Accessible.__bases__ = (Node,) + Accessibility.Accessible.__bases__
Accessibility.Application.__bases__ = (Application,) + Accessibility.Application.__bases__
Accessibility.Desktop.__bases__ = (Root,) + Accessibility.Desktop.__bases__

try:
    root = pyatspi.Registry.getDesktop(0)
    root.debugName= 'root'
except Exception:
    # Warn if AT-SPI's desktop object doesn't show up.
    logger.log("Error: AT-SPI's desktop is not visible. Do you have accessibility enabled?")

# Check that there are applications running. Warn if none are.
children = root.children
if not children:
    logger.log("Warning: AT-SPI's desktop is visible but it has no children. Are you running any AT-SPI-aware applications?")
del children

# Convenient place to set some debug variables:
#config.debugSearching = True
#config.absoluteNodePaths = True
#config.logDebugToFile = False

