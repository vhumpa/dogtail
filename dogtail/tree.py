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
class is a wrapper around Accessible and the various Accessible interfaces.

The Action class represents an action that the accessibility layer exports as
performable on a specific node, such as clicking on it. It's a wrapper around
AccessibleAction.

We often want to look for a node, based on some criteria, and this is provided
by the Predicate class.

Dogtail implements a high-level searching system, for finding a node (or
nodes) satisfying whatever criteria you are interested in.      It does this with
a 'backoff and retry' algorithm. This fixes most timing problems e.g. when a
dialog is in the process of opening but hasn't yet done so.

If a search fails, it waits 'config.searchBackoffDuration' seconds, and then
tries again, repeatedly. After several failed attempts (determined by
config.searchWarningThreshold) it will start sending warnings about the search
to the debug log. If it still can't succeed after 'config.searchCutoffCount'
attempts, it raises an exception containing details of the search. You can see
all of this process in the debug log by setting 'config.debugSearching' to True

We also automatically add a short delay after each action
('config.defaultDelay' gives the time in seconds).      We'd hoped that the search
backoff and retry code would eliminate the need for this, but unfortunately we
still run into timing issues.    For example, Evolution (and probably most
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

from utils import checkForA11y
checkForA11y()

import re
import predicate
from datetime import datetime
from time import sleep
from config import config
from utils import doDelay
from utils import Blinker
import rawinput
import path

from logging import debugLogger as logger

try:
    import atspi
except ImportError:
    # If atspi can't be imported, fail.
    raise ImportError, "Error importing the AT-SPI bindings"

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

class ReadOnlyError(TypeError):
    """
    This attribute is not writeable.
    """
    message = "Cannot set %s. It is read-only."
    def __init__(self, attr):
        self.attr = attr

    def __str__(self):
        return self.message % self.attr

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

    def __getattr__ (self, attr):
        if attr == "name":
            return self.__action.getName (self.__index).lower()
        elif attr == "description":
            return self.__action.getDescription (self.__index)
        elif attr == "keyBinding":
            return self.__action.getKeyBinding (self.__index)
        else: raise AttributeError, attr

    def __str__ (self):
        """
        Plain-text representation of the Action.
        """
        string = "Action node='%s' name='%s' description='%s' keybinding='%s'" % (self.node, self.name, self.description, self.keyBinding)
        return string

    def do (self):
        """
        Performs the given tree.Action, with appropriate delays and logging.
        """
        assert isinstance(self, Action)
        logger.log("%s on %s"%(self.name, self.node.getLogString()))
        if not self.node.sensitive:
            if config.ensureSensitivity:
                raise NotSensitiveError, self
            else:
                nSE = NotSensitiveError(self)
                logger.log("Warning: " + str(nSE))
        if config.blinkOnActions: self.node.blink()
        result = self.__action.doAction (self.__index)
        doDelay()
        return result

class Node:
    """
    A node in the tree of UI elements. It wraps an Accessible and
    exposes its useful members. It also has a debugName which is set
    up automatically when doing searches.

    Node instances have various attributes synthesized, to make it easy to
    get and the underlying accessible data. Many more attributes can be
    added as desired.

    'name' (read-only string):
    Wraps Accessible_getName on the Node's underlying Accessible

    'roleName' (read-only string):
    Wraps Accessible_getRoleName on the Node's underlying Accessible

    'role' (read-only atspi role enum):
    Wraps Accessible_getRole on the Node's underlying Accessible

    'description' (read-only string):
    Wraps Accessible_getDescription on the Node's underlying Accessible

    'parent' (read-only Node instance):
    A Node instance wrapping the parent, or None. Wraps Accessible_getParent

    'children' (read-only list of Node instances):
    The children of this node, wrapping getChildCount and getChildAtIndex

    'text' (string):
    For instances wrapping AccessibleText, the text. This is read-only,
    unless the instance wraps an AccessibleEditableText. In this case, you
    can write values to the attribute. This will get logged in the debug
    log, and a delay will be added. After the delay, the content of the
    node will be checked to ensure that it has the expected value. If it
    does not, an exception will be raised. This does not work for password
    dialogs (since all we get back are * characters). In this case, set
    the passwordText attribute instead.

    'passwordText' (write-only string):
    See documentation of 'text' attribute above.

    'caretOffset' (read/write int):
    For instances wrapping AccessibleText, the location of the text caret,
    expressed as an offset in characters.

    'combovalue' (write-only string):
    For comboboxes. Write to this attribute to set the combobox to the
    given value, with appropriate delays and logging.

    'stateSet' (read-only StateSet instance):
    Wraps Accessible_getStateSet; a set of boolean state flags

    'relations' (read-only list of atspi.Relation instances):
    Wraps Accessible_getRelationSet

    'labellee' (read-only list of Node instances):
    The node(s) that this node is a label for. Generated from 'relations'.

    'labeller' (read-only list of Node instances):
    The node(s) that is/are a label for this node. Generated from
    'relations'.

    'checked' (read-only boolean):
    Is this node checked? Only valid for checkboxes. Generated from stateSet
    based on presence of atspi.SPI_STATE_CHECKED.

    'sensitive' (read-only boolean):
    Is this node sensitive (i.e. not greyed out). Generated from stateSet
    based on presence of atspi.SPI_STATE_SENSITIVE
    Not all applications/toolkits seem to properly set this up.

    'showing' (read-only boolean):
    Generated from stateSet based on presence of atspi.SPI_STATE_SHOWING

    'focusable' (read-only boolean):
    Generated from stateSet based on presence of atspi.SPI_STATE_FOCUSABLE

    'focused' (read-only boolean):
    Generated from stateSet based on presence of atspi.SPI_STATE_FOCUSED

    'actions' (read-only list of Action instances):
    Generated from Accessible_getAction and AccessibleAction_getNActions

    For each action that is supported by a node, a method is hooked up,
    this can include the following list:
    'click'
    'press'
    'release'
    'activate'
    'jump'
    'check'
    'dock'
    'undock'
    'open'
    'menu'

    'extents' (readonly tuple):
    For instances wrapping a Component, the (x,y,w,h) screen extents of the
    component.

    'position' (readonly tuple):
    For instances wrapping a Component, the (x,y) screen position of the
    component.

    'size' (readonly tuple):
    For instances wrapping a Component, the (w,h) screen size of the component.

    'grabFocus':
    For instances wrapping a Component, attempt to set the keyboard input focus
    to that Node.

    'toolkit' (readonly string):
    For instances wrapping an application, the name of the toolkit.

    'version'
    For instances wrapping an application.

    'ID'
    For instances wrapping an application.

    'pause' (function)
    'resume' (function)
    For instances wrapping an application; probably don't work
    """

    #Valid types of AT-SPI objects we wrap.
    contained = ('__accessible', '__action', '__component', '__text', '__editableText', '__selection')

    def __init__ (self, initializer):
        self.__hideChildren = False
        self.debugName = None
        if isinstance(initializer, atspi.Accessible):
            self.__accessible = initializer
        elif isinstance(initializer, Node):
            self.__accessible = initializer.__accessible
            self.debugName = getattr(initializer, 'debugName', None)
        else:
            raise "Unknown Node initializer"
        assert self.__accessible

        # Swallow the Action object, if it exists
        self.__action = self.__accessible.getAction()
        if self.__action is not None:
            def doAction(name):
                """
                Performs the tree.Action with the given name, with appropriate delays and logging,
                or raises the ActionNotSupported exception if the node doesn't support that particular
                action.
                """
                actions = self.actions
                if actions.has_key(name):
                    return actions[name].do()
                else:
                    raise ActionNotSupported(name, self)
            self.doAction = doAction

        # Swallow the Component object, if it exists
        self.__component = self.__accessible.getComponent()
        if self.__component is not None:
            def grabFocus():
                self.__component.grabFocus()
                doDelay()
            self.grabFocus = grabFocus

            def rawClick(button = 1):
                """
                Generates a raw mouse click event whether or not the Node has a 'click' action, using the specified button.
                1 is left,
                2 is middle,
                3 is right.
                """
                extents = self.extents
                position = (extents[0], extents[1])
                size = (extents[2], extents[3])
                clickX = position[0] + 0.5 * size[0]
                clickY = position[1] + 0.5 * size[1]
                if config.debugSearching:
                    logger.log("raw click on %s %s at (%s,%s)"%(self.name, self.getLogString(), str(clickX), str(clickY)))
                rawinput.click(clickX, clickY, button)
            self.rawClick = rawClick

        # Swallow the Text object, if it exists
        self.__text = self.__accessible.getText()
        if self.__text is not None:
            self.addSelection = self.__text.addSelection
            self.getNSelections = self.__text.getNSelections
            self.removeSelection = self.__text.removeSelection
            self.setSelection = self.__text.setSelection

        # Swallow the EditableText object, if it exists
        self.__editableText = self.__accessible.getEditableText()
        if self.__editableText is not None:
            self.setAttributes = self.__editableText.setAttributes

        # Swallow the Hypertext object, if it exists
        self.__hypertext = self.__accessible.getHypertext()

        # Swallow the Selection object, if it exists
        self.__selection = self.__accessible.getSelection()
        if self.__selection is not None:
            def selectAll():
                """
                Selects all children.
                """
                return self.__selection.selectAll()
            self.selectAll = selectAll

            def deselectAll():
                """
                Deselects all selected children.
                """
                return self.__selection.clearSelection()
            self.deselectAll = deselectAll

        # Implement select() for children of nodes with Selection interfaces.
        parent = self.parent
        if parent and parent._Node__selection:
            def select():
                """
                Selects the node, relative to its siblings.
                """
                return self.parent._Node__selection.selectChild(self.indexInParent)
            self.select = select

            def deselect():
                """
                Deselects the node, relative to its siblings.
                """
                selectedIndex = 0
                parent = self.parent
                for i in range(self.indexInParent):
                    if parent.children[i].isSelected:
                        selectedIndex+=1
                return parent._Node__selection.deselectSelectedChild(selectedIndex)
            self.deselect = select

        # Add more objects here. Nobody uses them yet, so I haven't.
        # You also need to change the __getattr__ and __setattr__ functions.

    # It'd be nice to know if two objects are "identical". However, the
    # approach below does not work, since atspi.Accessible doesn't know
    # how to check if two cspi.Accessible objects are "identical" either. :(
    #def __cmp__ (self, node):
    #        return self.__accessible == node.__accessible

    def __getattr__ (self, attr):
        if False: pass

        # Attributes from Applications
        # (self.__accessible will be an Application and not an Accessible)
        elif attr == "toolkit" and type(self.__accessible) == atspi.Application:
            return self.__accessible.getToolkit()
        elif attr == "version" and type(self.__accessible) == atspi.Application:
            return self.__accessible.getVersion()
        elif attr == "ID" and type(self.__accessible) == atspi.Application:
            return self.__accessible.getID()
        # These two appear to be useless, so they're lazily bound. :)
        elif attr == "pause" and type(self.__accessible) == atspi.Application:
            return self.__accessible.pause
        elif attr == "resume" and type(self.__accessible) == atspi.Application:
            return self.__accessible.resume

        # Attributes from the Accessible object
        elif attr == "name":
            return self.__accessible.getName()
        elif attr == "role":
            return self.__accessible.getRole()
        elif attr == "roleName":
            return self.__accessible.getRoleName()
        elif attr == "description":
            return self.__accessible.getDescription()
        elif attr == "parent":
            parentAcc = self.__accessible.getParent ()
            if parentAcc:
                parent = Node (parentAcc)
                return parent
        elif attr =="indexInParent":
            return self.__accessible.getIndexInParent()
        elif attr == "children":
            if self.__hideChildren: return []
            children = []
            childCount = self.__accessible.getChildCount()
            if childCount > config.childrenLimit:
                global haveWarnedAboutChildrenLimit
                if not haveWarnedAboutChildrenLimit:
                    logger.log("Only returning %s children. You may change config.childrenLimit if you wish. This message will only be printed once." % str(config.childrenLimit))
                    haveWarnedAboutChildrenLimit = True
                childCount = config.childrenLimit
            for i in xrange (childCount):
                if isinstance(self, Root):
                    try: a = self.__accessible.getChildAtIndex (i)
                    except atspi.SpiException:
                        import traceback
                        logger.log(traceback.format_exc())
                else: a = self.__accessible.getChildAtIndex (i)
                # Workaround to GNOME bug #321273
                # http://bugzilla.gnome.org/show_bug.cgi?id=321273
                if a is not None: children.append (Node (a))
            # Attributes from the Hypertext object
            if self.__hypertext:
                for i in range(self.__hypertext.getNLinks()):
                    children.append(Link(self, self.__hypertext.getLink(i), i))
            return children
        elif attr == "stateSet":
            return self.__accessible.getStateSet()
        elif attr == "relations":
            return self.__accessible.getRelationSet()
        elif attr == "labellee":
            # Find the nodes that this node is a label for:
            # print self.relations
            for relation in self.relations:
                if relation.getRelationType() == atspi.SPI_RELATION_LABEL_FOR:
                    targets = relation.getTargets ()
                    return apply(Node, targets)
        elif attr == "labeller":
            # Find the nodes that are a label for this node:
            # print self.relations
            for relation in self.relations:
                if relation.getRelationType() == atspi.SPI_RELATION_LABELED_BY:
                    targets = relation.getTargets ()
                    return apply(Node, targets)

        # Attributes synthesized from the Accessible's stateSet:
        elif attr == "sensitive":
            return self.__accessible.getStateSet().contains(atspi.SPI_STATE_SENSITIVE)
        elif attr == "showing":
            return self.__accessible.getStateSet().contains(atspi.SPI_STATE_SHOWING)
        elif attr == "focusable":
            return self.__accessible.getStateSet().contains(atspi.SPI_STATE_FOCUSABLE)
        elif attr == "focused":
            return self.__accessible.getStateSet().contains(atspi.SPI_STATE_FOCUSED)
        elif attr == "checked":
            return self.__accessible.getStateSet().contains(atspi.SPI_STATE_CHECKED)

        # Attributes from the Action object
        elif attr == "actions":
            actions = {}
            if self.__action:
                for i in xrange (self.__action.getNActions ()):
                    action = (Action (self, self.__action, i))
                    actions[action.name] = action
            return actions

        # Attributes from the Component object
        elif attr == "extents":
            if self.__component:
                return self.__component.getExtents()
        elif attr == "position":
            if self.__component:
                return self.__component.getPosition()
        elif attr == "size":
            if self.__component:
                # This always returns [0, 0]
                #return self.__component.getSize()
                extents = self.__component.getExtents()
                size = (extents[2], extents[3])
                return size

        # Attributes from the Text object
        elif attr == "text":
            if self.__text:
                return self.__text.getText(0, 32767)
        elif attr == "caretOffset":
            if self.__text:
                return self.__text.getCaretOffset()

        # Attributes from the Selection object
        elif attr == "isSelected":
            parent = self.parent
            if parent and parent._Node__selection:
                return self.parent._Node__selection.isChildSelected(self.indexInParent)
        elif attr == "selectedChildren":
            if self.__hideChildren:
                return []
            selectedChildren = []
            if self.__selection:
                for i in xrange(self.__selection.getNSelectedChildren()):
                    selectedChildren.append(Node(self.__selection.getSelectedChild(i)))
            return selectedChildren

        else: raise AttributeError, attr

    def __setattr__ (self, attr, value):
        if False: pass

        # Are we swallowing an AT-SPI object?
        elif attr.replace('_Node', '') in self.contained:
            self.__dict__[attr] = value

        # Read-only attributes from Applications
        # (self.__accessible will be an Application and not an Accessible)
        elif attr in ["toolkit", "version", "ID"]:
            raise ReadOnlyError, attr

        # Read-only attributes from the Accessible object
        elif attr in ["name", "role", "roleName", "description", "parent",
                      "indexInParent", "children", "stateSet", "relations",
                      "labellee", "labeller"]:
            raise ReadOnlyError, attr

        # Read-only attributes synthesized from the Accessible's stateSet:
        elif attr in ["sensitive", "showing", "focusable", "focused", "checked"]:
            raise ReadOnlyError, attr

        # Read-only attributes from the Action object
        elif attr == "actions":
            raise ReadOnlyError, attr

        # Attributes from the Component object
        elif attr in ["extents", "position", "size"]:
            raise ReadOnlyError, attr

        # Attributes from the Text object
        elif attr=="caretOffset":
            if not self.__text:
                raise ReadOnlyError, attr
            self.__text.setCaretOffset(value)

        # Attributes from the EditableText object
        elif attr=="text":
            """
            Set the text of the node to the given value, with
            appropriate delays and logging, then test the result:
            """
            if not self.__editableText:
                raise ReadOnlyError, attr
            if config.debugSearching: logger.log("Setting text of %s to '%s'"%(self.getLogString(), value))
            self.__editableText.setTextContents (value)
            doDelay()

            #resultText = self.text
            #if resultText != value:
            #       raise "%s failed to have its text set to '%s'; value is '%s'"%(self.getLogString(), value, resultText)

        elif attr=='passwordText':
            """
            Set the text of the node to the given value, with
            appropriate delays and logging. We can't test the
            result, we'd only get * characters back.
            """
            if not self.__editableText:
                raise ReadOnlyError, attr
            logger.log("Setting text %s to password '%s'"%(self.getLogString(), value))
            self.__editableText.setTextContents (value)
            doDelay()

        elif attr=="combovalue":
            """
            Set the combobox to the given value, with appropriate delays and
            logging.
            """
            logger.log("Setting combobox %s to '%s'"%(self.getLogString(), value))
            self.childNamed(childName=value).click()
            doDelay()
        else:
            # FIXME: should we doing stuff like in the clause above???
            self.__dict__[attr] = value

    def typeText(self, string):
        """
        Type the given text into the node, with appropriate delays and
        logging.
        """
        logger.log("Typing text into %s: '%s'"%(self.getLogString(), string))

        # Non-working implementation
        # Unfortunately, the call to AccessibleText_setCaretOffset fails for Evolution's gtkhtml composer for some reason
        if False:
            logger.log("caret offset: %s" % self.caretOffset)
            self.__editableText.insertText (self.caretOffset, text)
            self.caretOffset+=len(string) # FIXME: is this correct?
            logger.log("new caret offset: %s" % self.caretOffset)

        if self.focusable:
            if not self.focused:
                try: self.grabFocus()
                except: logger.log("Node is focusable but I can't grabFocus!")
            rawinput.typeText(string)
        else:
            logger.log("Node is not focusable; falling back to setting text")
            node.text += string
            doDelay()

    def keyCombo(self, comboString):
        if config.debugSearching: logger.log("Pressing keys '%s' into %s"%(combo, self.getLogString()))
        if self.focusable:
            if not self.focused:
                try: self.grabFocus()
                except: logger.log("Node is focusable but I can't grabFocus!")
        else: logger.log("Node is not focusable; trying key combo anyway")
        rawinput.keyCombo(comboString)

    def __str__ (self):
        """
        If debugName is set on this Node, returns debugName surrounded
        in curly braces.
        Otherwise, returns a plain-text representation of the most
        important attributes of the underlying Accessible.
        """
        if self.debugName:
            return "{" + self.debugName + "}"
        else:
            string = "Node"
            string = string + " roleName='%s'" % self.roleName
            string = string + " name='%s' description='%s'" % (self.name, self.description)
            if self.text is not None:
                string = string + " text='%s'" % self.text
            return string

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

    def dump (self, type = 'plain'):
        import dump
        dumper = getattr (dump, type)
        dumper (self)

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

    # The canonical search method:
    def findChild(self, pred, recursive = True, debugName = None, retry = True, requireResult = True):
        """
        Search for a node satisyfing the predicate, returning a Node.

        If retry is True (the default), it makes multiple attempts,
        backing off and retrying on failure, and eventually raises a
        descriptive exception if the search fails.

        If retry is False, it gives up after one attempt.

        If requireResult is True (the default), an exception is raised after all
        attempts have failed. If it is false, the function simply returns None.

        FIXME: make multiple attempts?
        """

        def findFirstChildSatisfying (parent, pred, recursive = True):
            """
            Internal helper function that does a one-shot search, recursing if need be.
            """
            # print "findFirstChildSatisfying(%s, %s, recursive=%s)"%(parent, pred,recursive)
            assert isinstance(pred, predicate.Predicate)

            try: children = parent.children
            except: return None

            for child in children:
                # print child
                if child.satisfies(pred):
                    return child
                else:
                    if recursive:
                        child = findFirstChildSatisfying(child, pred, recursive)
                        if child: return child
                # ...on to next child

        def describeSearch (parent, pred, recursive, debugName):
            """
            Internal helper function
            """
            if recursive:
                noun = "descendent"
            else:
                noun = "child"

            if debugName == None:
                debugName = pred.describeSearchResult()

            return "%s of %s: %s"%(noun, parent.getLogString(), debugName)

        assert isinstance(pred, predicate.Predicate)
        numAttempts = 0
        while numAttempts<config.searchCutoffCount:
            if numAttempts>=config.searchWarningThreshold or config.debugSearching:
                logger.log("searching for %s (attempt %i)" % (describeSearch(self, pred, recursive, debugName), numAttempts))

            result = findFirstChildSatisfying(self, pred, recursive)
            if result:
                assert isinstance(result, Node)
                if debugName:
                    result.debugName = debugName
                else:
                    result.debugName = pred.describeSearchResult()
                return result
            else:
                if not retry: break
                numAttempts+=1
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
        assert isinstance(pred, predicate.Predicate)

        selfList = []


        try: children = self.children
        except: return []

        for child in children:
            if child.satisfies(pred): selfList.append(child)
            if recursive:
                childList = child.findChildren(pred, recursive)
                if childList:
                    for child in childList:
                        selfList.append(child)
            # ...on to next child

        if selfList: return selfList

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

    # FIXME: does this clash with the "menu" action
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
        except: return result
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


    def click(self):
        """
        If the Node supports an action called "click", do it, with appropriate delays and logging.
        Otherwise, raise an ActionNotSupported exception.

        Note that this is just a shortcut to doAction('click'), as it is by far the most-used
        action. To do any other action such as 'activate' or 'open', you must use doAction().
        """
        if self.__action is not None:
            return self.doAction('click')
        raise ActionNotSupported('click', self)

class Link(Node):
    """
    Class representing a hyperlink
    """
    contained = ('__hyperlink', '__node')

    def __init__(self, node, hyperlink, index):
        self.debugName = None
        self.parent = node
        self.__hyperlink = hyperlink
        self.__index = index
        self.__node = Node(self.__hyperlink.getObject(self.__index))
        # Somehow, if we allow the children to be seen, things get weird.
        self.__node.__hideChildren = True

    def __getattr__(self, name):
        if False: pass
        elif name == 'URI':
            # Note: This doesn't seem to work. It usually just causes python to hang.
            return self.__hyperlink.getURI(self.__index)
        else:
            if name == 'children':
                return []
            try:
                result = getattr(self.__node, name)
                return result
            except AttributeError:
                raise AttributeError, name

    def __setattr__(self, name, value):
        self.__dict__[name] = value

class Root (Node):
    """
    FIXME:
    """
    def applications(self):
        """
        Get all applications.
        """
        return root.findAllChildrenSatisfying(predicate.GenericPredicate(roleName="application"), recursive=False)

    def application(self, appName):
        """
        Gets an application by name, returning an Application instance
        or raising an exception.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """
        return Application(root.findChild(predicate.IsAnApplicationNamed(appName),recursive=False))

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
        result = Window(self.findChild (predicate.IsAWindowNamed(windowName=windowName), recursive))
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

try:
    root = Root (atspi.registry.getDesktop ())
    root.debugName= 'root'
except AssertionError:
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
