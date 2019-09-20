# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from dogtail.config import config
from dogtail import path
from dogtail import predicate
from dogtail import rawinput
from dogtail.rawinput import ponytail
from dogtail.logging import debug_message, info_message
from dogtail.utils import doDelay, Blinker, Lock
from dogtail.rawinput import SESSION_TYPE, ponytail_check_is_xwayland

from time import sleep
from types import LambdaType
import gi
from gi.repository import GLib
import os
import sys

"""
Makes some sense of the AT-SPI API

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
"""

__author__ = """Zack Cerza <zcerza@redhat.com>,
                David Malcolm <dmalcolm@redhat.com>
"""

try:
    import pyatspi
    import Accessibility
except ImportError:  # pragma: no cover
    raise ImportError("Error importing the AT-SPI bindings")


if config.checkForA11y:
    from dogtail.utils import checkForA11y
    checkForA11y()


# We optionally import the bindings for libWnck.
try:
    gi.require_version("Wnck", "3.0")
    from gi.repository import Wnck
    gotWnck = True  # pragma: no cover
except (ImportError, ValueError):
    # Skip this warning, since the functionality is almost entirely nonworking anyway.
    # print "Warning: Dogtail could not import the Python bindings for
    # libwnck. Window-manager manipulation will not be available."
    gotWnck = False


haveBeenWarnedAboutActionTypes = False
haveWarnedAboutChildrenLimit = False


class SearchError(Exception):
    """
    The widget was not found.
    """


class NotSensitiveError(Exception):
    """
    The widget is not sensitive.
    """

    def __init__(self, action):
        debug_message(message="Not Sensitive Error Exception")

        self.message = "Cannot %s %s. It is not sensitive."
        self.action = action


    def __str__(self):
        return self.message % (self.action.name, self.action.node.getLogString())


class ActionNotSupported(Exception):
    """
    The widget does not support the requested action.
    """

    def __init__(self, actionName, node):
        debug_message(message="Action Not Supported Exception")

        self.message = "Cannot do '%s' action on %s"
        self.actionName = actionName
        self.node = node


    def __str__(self):
        return self.message % (self.actionName, self.node.getLogString())


class Action(object):
    """
    Class representing an action that can be performed on a specific node.
    """

    def __init__(self, node, action, index):
        self.types = ("click", "press", "release", "activate", \
            "jump", "check", "dock", "undock", "open", "menu")

        global haveBeenWarnedAboutActionTypes
        if not haveBeenWarnedAboutActionTypes:
            debug_message(message="Valid types of actions we know about.\n'%s'.\n" % ",".join(self.types))
            debug_message(message="Feel free to add any you see.")
            haveBeenWarnedAboutActionTypes = True

        self.node = node
        self.__action = action
        self.__index = index


    @property
    def name(self):
        return self.__action.getName(self.__index)


    @property
    def description(self):
        return self.__action.getDescription(self.__index)


    @property
    def keyBinding(self):
        return self.__action.getKeyBinding(self.__index)


    def __str__(self):
        return "[action | %s | %s ]" % (self.name, self.keyBinding)


    def do(self):
        """
        Performs the given tree.Action, with appropriate delays and logging.
        """

        debug_message(message="Performing action '%s' on '%s'" % \
            (str(self.name), self.node.getLogString()))

        if not self.node.sensitive:
            if config.ensureSensitivity:
                raise NotSensitiveError(self)
            else:
                debug_message(message="Warning " + str(NotSensitiveError(self)))

        if config.blinkOnActions:
            self.node.blink()

        result = self.__action.doAction(self.__index)
        doDelay(config.actionDelay)

        return result


class Node(object):
    """
    A node in the tree of UI elements. This class is mixed in with
    Accessibility.Accessible to both make it easier to use and to add
    additional functionality. It also has a debugName which is set up
    automatically when doing searches.
    """

    def __setupUserData(self):
        """
        Setup user data dictionary.
        """
        try:
            len(self.user_data)
        except (AttributeError, TypeError):
            self.user_data = {}


    @property
    def debugName(self):
        """
        Debug name assigned during search operations.
        """

        self.__setupUserData()
        return self.user_data.get("debugName", None)


    @debugName.setter
    def debugName(self, debugName):
        """
        Debug name setter.
        """

        self.__setupUserData()
        self.user_data["debugName"] = debugName


    @property
    def dead(self):
        """
        Is the node dead (defunct)?
        """

        debug_message(message="Node.dead() - checking if node is dead.")

        try:
            if self.roleName == "invalid":
                return True
            assert self.role is not None
            assert self.name is not None
            if len(self) > 0:
                assert self.children[0] is not None
        except Exception:
            return True
        return False


    @property
    def children(self):
        """
        A list of this Accessible's children.
        """

        debug_message(message="Node.children - returns all children in the list.")

        if self.parent and self.parent.roleName == "hyper link":
            debug_message(message=self.parent.role)
            return []

        children_list = []
        childCount = self.childCount
        if childCount > config.childrenLimit:
            global haveWarnedAboutChildrenLimit
            if not haveWarnedAboutChildrenLimit:
                debug_message(message="Only returning '%s' children." % str(config.childrenLimit))
                debug_message(message="You may change config.childrenLimit if you wish.")
                debug_message(message="This message will only be printed once.")
                haveWarnedAboutChildrenLimit = True
                childCount = config.childrenLimit

        for i in range(childCount):
            """
            Workaround for GNOME bug #465103
            also solution for GNOME bug #321273
            """

            try:
                child = self[i]
            except LookupError:
                child = None

            if child:
                children_list.append(child)

        invalidChildren = childCount - len(children_list)
        if invalidChildren and config.debugSearching:
            debug_message(message="Skipped '%s' children of '%s' as they are over config.childrenLimit" % \
                (invalidChildren, str(self)))

        try:
            ht = self.queryHypertext()
            for li in range(ht.getNLinks()):
                link = ht.getLink(li)
                for ai in range(link.nAnchors):
                    child = link.getObject(ai)
                    if child == self:
                        continue
                    child.__setupUserData()
                    child.user_data['linkAnchor'] = \
                        LinkAnchor(node=child,
                                   hypertext=ht,
                                   linkIndex=li,
                                   anchorIndex=ai)
                    children.append(child)
        except (NotImplementedError, AttributeError):
            pass

        return children_list


    roleName = property(Accessibility.Accessible.getRoleName)
    role = property(Accessibility.Accessible.getRole)
    name = property(Accessibility.Accessible.name)
    parent = property(Accessibility.Accessible.parent)
    indexInParent = property(Accessibility.Accessible.getIndexInParent)
    __window_id = None


    @property
    def window_id(self):
        """
        Return window id of a node.
        """

        debug_message(message="Node.window_id - returns window id.")

        if SESSION_TYPE == "x11":
            return None

        if self.__window_id is None:
            debug_message(message="Window id event.")

            window_list = ponytail.window_list
            if len(window_list) == 0:
                doDelay(config.actionDelay)
                window_list = ponytail.window_list

            for window in window_list:
                if "title" not in window.keys():
                    window["title"] = ""

            node = self
            parent_list = [node]
            while node.parent is not None:
                parent_list.append(node.parent)
                node = node.parent

            for ancestor in parent_list:
                if ancestor.parent is None:
                    self.__window_id = [x["id"] for x in window_list if bool(x["has-focus"]) is True][0]
                    return [x["id"] for x in window_list if bool(x["has-focus"]) is True][0]

                elif ancestor.parent.roleName == "application" and ancestor.parent.name == "gnome-shell":
                    return ""

                elif ancestor.parent.roleName == "application" and ancestor.roleName == "window" and ancestor.name == "":
                    self.__window_id = [x["id"] for x in window_list if bool(x["has-focus"]) is True][0]
                    return [x["id"] for x in window_list if bool(x["has-focus"]) is True][0] # context menus

                elif ancestor.parent.roleName == "application" and ancestor.name in [x["title"] for x in window_list]:
                    self.__window_id = [x["id"] for x in window_list if x["title"] == ancestor.name][0]
                    return [x["id"] for x in window_list if x["title"] == ancestor.name][0]

                elif ancestor.parent.roleName == "application":
                    self.__window_id = [x["id"] for x in window_list if bool(x["has-focus"]) is True][0]
                    return [x["id"] for x in window_list if bool(x["has-focus"]) is True][0]

        else:
            return self.__window_id


    @property
    def window_has_focus(self):
        """
        Check if window is focused.
        """

        debug_message(message="Node.window_has_focus - checks if window has focus.")

        if SESSION_TYPE == "wayland":
            window_id = self.window_id

            window_list = ponytail.window_list
            for window in window_list:
                if window["id"] == window_id and bool(window["has-focus"]) is True:
                    return True

            return False

        else:
            raise NotImplementedError


    def doActionNamed(self, name):
        """
        Perform the action with the specified name. For a list of actions
        supported by this instance, check the 'actions' property.
        """

        debug_message(message="Node.doActionNamed - make an action: " + name)

        actions = self.actions
        if name in actions:
            return actions[name].do()

        raise ActionNotSupported(name, self)


    @property
    def actions(self):
        """
        A dictionary of supported action names as keys, with Action objects as
        values. Common action names include:
            'click' 'press' 'release' 'activate' 'jump'
            'check' 'dock' 'undock' 'open' 'menu'
        """

        debug_message(message="Node.actions - returns all actions available.")

        actions = {}

        try:
            action_query = self.queryAction()
            for index in range(action_query.nActions):
                action_object = Action(self, action_query, index)
                actions[action_query.getName(index)] = action_object
        finally:
            debug_message(message="If actions are empty there could have been an exception.")
            return actions


    @property
    def combovalue(self):
        """
        The value (as a string) currently selected in the combo box.
        """

        debug_message(message="Node.combovalue - returns string value currently selected in the combo box.")

        return self.name


    @combovalue.setter
    def combovalue(self, value):
        debug_message(message="Setting combo box '%s' to value '%s." % \
            (self.getLogString(), str(value)))

        self.childNamed(childName=value).doActionNamed("click")
        doDelay()


    @property
    def URI(self):
        """
        The value of user data linkAnchor.
        """

        debug_message(message="Node.URI - returns string value of user data linkAnchor.")

        try:
            return self.user_data["linkAnchor"].URI
        except (KeyError, AttributeError):
            raise NotImplementedError


    @property
    def text(self):
        """
        For instances with an AccessibleText interface, the text as a
        string. This is read-only, unless the instance also has an
        AccessibleEditableText interface. In this case, you can write values
        to the attribute. This will get logged in the debug log, and a delay
        will be added.

        If this instance corresponds to a password entry, use the passwordText
        property instead.
        """

        debug_message(message="Node.text - returns string value of text attribute.")

        try:
            return self.queryText().getText(0, -1)
        except NotImplementedError:
            return None


    @text.setter
    def text(self, text):
        try:
            if config.debugSearching:
                setter_message = "Setting text of %s to '%s'"

                debug_message(message="Maximum length is set at 140, cutting the text after.")
                if len(text) > 140:
                    txt = text[:134] + " [...]"
                else:
                    txt = text

                debug_message(message=str(setter_message) % (self.getLogString(), str(txt)))

            self.queryEditableText().setTextContents(text)
        except NotImplementedError:
            raise AttributeError("can't set attribute")


    @property
    def caretOffset(self):
        """
        For instances with an AccessibleText interface, the caret offset as an integer.
        """

        debug_message(message="Node.caretOffset - returns caret offset of an integer.")

        return self.queryText().caretOffset


    @caretOffset.setter
    def caretOffset(self, offset):
        """
        Caret offset setter.
        """

        debug_message(message="Caret offset setter.")

        return self.queryText().setCaretOffset(offset)


    @property
    def position(self):
        """
        A tuple containing the position of the Accessible: (x, y)
        """

        debug_message(message="Node.position - returns position of the Accessible.")

        return self.queryComponent().getPosition(pyatspi.DESKTOP_COORDS)


    @property
    def size(self):
        """
        A tuple containing the size of the Accessible: (w, h)
        """

        debug_message(message="Node.size - returns size of the Accessible.")

        if SESSION_TYPE == "wayland":
            if self.roleName == "window" or self.roleName == "dialog" or self.roleName == "frame":
                window_list = ponytail.window_list
                window_id = self.window_id
                for window in window_list:
                    if window["id"] == window_id:
                        return (int(window["width"]), int(window["height"]))

        return self.queryComponent().getSize()


    @property
    def extents(self):
        """
        A tuple containing the location and size of the Accessible: (x, y, w, h)
        """

        debug_message(message="Node.extents - returns a tuple containing position and size of the Accessible.")

        try:
            ex = self.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
            return (ex.x, ex.y, ex.width, ex.height)
        except NotImplementedError:
            return None


    def contains(self, x, y):
        """
        Can tell if and x and y coordinates are inside a desktop coordinates.
        """

        debug_message(message="Node.contains - returns a bool if the x and y are inside a desktop coords.")

        try:
            return self.queryComponent().contains(x, y, pyatspi.DESKTOP_COORDS)
        except NotImplementedError:
            return False


    def getChildAtPoint(self, x, y):
        """
        Get a child in coordinates x, y.
        """

        debug_message(message="Node.getChildAtPoint - returns a child in x, y coordinates.")

        node = self
        while True:
            try:
                child = node.queryComponent().getAccessibleAtPoint(x, y, pyatspi.DESKTOP_COORDS)
                if child and child.contains(x, y):
                    node = child
                else:
                    break
            except NotImplementedError:
                break

        if node and node.contains(x, y):
            return node
        else:
            return None


    def grabFocus(self):
        """
        Attempts to set the keyboard focus to this Accessible.
        Affected by rhbz 1656447 on Wayland! We do different actions based on type of the node
        to get it focused there as workaround. For some we can do nothing (push button)
        """

        debug_message(message="Node.grabFocus - grabs focus of the Accessible object.")

        if SESSION_TYPE == "x11" or ponytail_check_is_xwayland(self.window_id) or self.window_has_focus:
            return self.queryComponent().grabFocus()

        else:
            if "toggle" in self.roleName or "check box" in self.roleName:
                self.doubleClick()

            elif "text" in self.roleName or "table cell" in self.roleName:
                self.click()

            elif "menu item" in self.roleName and self.position[0] > 0:
                self.select()

            elif "menu item" in self.roleName and self.findAncestor(predicate.GenericPredicate(roleName="combo box")):
                self.doActionNamed("click")

            else:
                pass


    def click(self, button=1):
        """
        Generates a raw mouse click event, using the specified button.
            - 1 is left,
            - 2 is middle,
            - 3 is right.
        """

        clickX = self.position[0] + self.size[0] / 2
        clickY = self.position[1] + self.size[1] / 2

        debug_message(message="""
            Node.click - clicking on a11y named '%s' on '%s' with coordinates '(%s, %s)'
        """ % (str(self.name), self.getLogString(), str(clickX), str(clickY)))

        if ("menu item" in self.roleName or self.roleName == "menu") and \
                self.parent.roleName != "menu bar" and \
                "click" in self.actions:
            self.select()

            doDelay(config.typingDelay)
            window_id = None
            if self.name.lower() in ["quit", "exit"] or "close" in self.name.lower():
                window_id = ""

            rawinput.pressKey("enter", window_id)
            doDelay(config.typingDelay)

        else:
            rawinput.click(clickX, clickY, button, window_id=self.window_id)


    def doubleClick(self, button=1):
        """
        Generates a raw mouse double-click event, using the specified button.
        """

        clickX = self.position[0] + self.size[0] / 2
        clickY = self.position[1] + self.size[1] / 2

        debug_message(message="""
            Node.doubleClick - double clicking on a11y named '%s' '%s' with coordinates '(%s, %s)'
        """ % (str(self.name), self.getLogString(), str(clickX), str(clickY)))

        rawinput.doubleClick(clickX, clickY, button, window_id=self.window_id)


    def point(self, mouseDelay=None):
        """
        Move mouse cursor to the center of the widget.
        """

        pointX = self.position[0] + self.size[0] / 2
        pointY = self.position[1] + self.size[1] / 2

        debug_message(message="""
            Node.point - pointing at a11y named '%s' '%s' with coordinates '(%s, %s)'
        """ % (str(self.name), self.getLogString(), str(pointX), str(pointY)))

        if "menu item" in self.roleName or self.roleName == "menu":
            debug_message(message="Local coords are OFF under \
                wayland for menu/context menu 'windows'.")
            self.select()
        else:
            rawinput.point(pointX, pointY, window_id=self.window_id)


    @property
    def labeler(self):
        """
        'labeller' (read-only list of Node instances):
        The node(s) that is/are a label for this node. Generated from 'relations'.
        """

        debug_message(message="Node.labeler - returns node(s) that is/are label for this node.")

        relationSet = self.getRelationSet()
        for relation in relationSet:
            if relation.getRelationType() == pyatspi.RELATION_LABELLED_BY:
                if relation.getNTargets() == 1:
                    return relation.getTarget(0)

                targets = []
                for i in range(relation.getNTargets()):
                    targets.append(relation.getTarget(i))

                return targets

    labeller = labeler


    @property
    def labelee(self):
        """
        'labellee' (read-only list of Node instances):
        The node(s) that this node is a label for. Generated from 'relations'.
        """

        debug_message(message="Node.labelee - returns node(s) that this node is label for.")

        relationSet = self.getRelationSet()
        for relation in relationSet:
            if relation.getRelationType() == pyatspi.RELATION_LABEL_FOR:
                if relation.getNTargets() == 1:
                    return relation.getTarget(0)

                targets = []
                for i in range(relation.getNTargets()):
                    targets.append(relation.getTarget(i))

                return targets


    labellee = labelee


    @property
    def sensitive(self):
        """
        Is the Accessible sensitive (i.e. not greyed out)?
        """

        debug_message(message="Node.sensitive - is the Accessible sensitive (i.e. not greyed out)?")

        return self.getState().contains(pyatspi.STATE_SENSITIVE)


    @property
    def showing(self):
        """
        Is the Accessible showing (rendered and visible) on the screen?
        """

        debug_message(message="Node.showing - is the Accessible showing (rendered and visible) on the screen?")

        return self.getState().contains(pyatspi.STATE_SHOWING)


    @property
    def focusable(self):
        """
        Is the Accessible capable of having keyboard focus?
        """

        debug_message(message="Node.focusable - is the Accessible capable of having keyboard focus?")

        return self.getState().contains(pyatspi.STATE_FOCUSABLE)


    @property
    def focused(self):
        """
        Does the Accessible have keyboard focus?
        """

        debug_message(message="Node.focused - does the Accessible have keyboard focus?")

        return self.getState().contains(pyatspi.STATE_FOCUSED)


    @property
    def checked(self):
        """
        Is the Accessible a checked checkbox?
        """

        debug_message(message="Node.checked - is the Accessible a checked checkbox?")

        return self.getState().contains(pyatspi.STATE_CHECKED)


    @property
    def isChecked(self):
        """
        Is the Accessible a checked checkbox? Compatibility property, same as Node.checked.
        """

        debug_message(message="Node.isChecked - compatibility property, same as Node.checked.")

        return self.checked


    @property
    def visible(self):
        """
        Is the Accessible set to be visible? A widget with set attribute
        'visible' is supposed to be shown and doesn't need to be actually
        rendered. On the other hand, a widget with unset attribute 'visible'
        """

        debug_message(message="Node.visible - is the Accessible set to be visible?")

        return self.getState().contains(pyatspi.STATE_VISIBLE)


    def selectAll(self):
        """
        Selects all children.
        """

        debug_message(message="Node.selectAll - selects all children.")

        result = self.querySelection().selectAll()
        doDelay()
        return result


    def deselectAll(self):
        """
        Deselects all selected children.
        """

        debug_message(message="Node.deselectAll - deselects all selected children.")

        result = self.querySelection().clearSelection()
        doDelay()
        return result


    def select(self):
        """
        Selects the Accessible.
        """

        debug_message(message="Node.select - selects the Accessible.")

        try:
            parent = self.parent
        except AttributeError:
            raise NotImplementedError

        result = parent.querySelection().selectChild(self.indexInParent)
        doDelay()
        return result


    def deselect(self):
        """
        Deselects the Accessible.
        """

        debug_message(message="Node.deselect - deselects the Accessible.")

        try:
            parent = self.parent
        except AttributeError:
            raise NotImplementedError

        result = parent.querySelection().deselectChild(self.indexInParent)
        doDelay()
        return result


    @property
    def isSelected(self):
        """
        Is the Accessible selected? Compatibility property, same as Node.selected.
        """

        debug_message(message="Node.isSelected - compatibility property, same as Node.selected.")

        try:
            parent = self.parent
        except AttributeError:
            raise NotImplementedError
        return parent.querySelection().isChildSelected(self.indexInParent)


    @property
    def selected(self):
        """
        Is the Accessible selected?
        """

        debug_message(message="Node.selected - is the Accessible selected?")

        return self.isSelected


    @property
    def selectedChildren(self):
        """
        Returns a list of children that are selected.
        """

        debug_message(message="Node.selectedChildren - returns a list of children that are selected.")

        selection = self.querySelection()

        selectedChildren = []
        for i in range(selection.nSelectedChildren):
            selectedChildren.append(selection.getSelectedChild(i))


    @property
    def value(self):
        """
        The value contained by the AccessibleValue interface.
        """

        debug_message(message="Node.value - returns the value contained by the AccessibleValue interface.")

        try:
            return self.queryValue().currentValue
        except NotImplementedError:
            pass


    @value.setter
    def value(self, value):
        """
        Setter for the value contained by the AccessibleValue interface.
        """

        debug_message(message="Setter for the value contained by the AccessibleValue interface.")

        self.queryValue().currentValue = value


    @property
    def minValue(self):
        """
        The minimum value of Node.value
        """

        debug_message(message="Node.minValue - returns the minimum value of Node.value.")

        try:
            return self.queryValue().minimumValue
        except NotImplementedError:
            pass


    @property
    def minValueIncrement(self):
        """
        The minimum value increment of the Node.value
        """

        debug_message(message="Node.minValueIncrement - returns the minimum value increment of the Node.value.")

        try:
            return self.queryValue().minimumIncrement
        except NotImplementedError:
            pass


    @property
    def maxValue(self):
        """
        The maximum value of self.value
        """

        debug_message(message="Node.maxValue - returns the maximum value of Node.value.")

        try:
            return self.queryValue().maximumValue
        except NotImplementedError:
            pass


    def typeText(self, string):
        """
        Type the given text into the node, with appropriate delays and logging.
        """

        debug_message(message="Node.typeText - typing text into '%s': '%s'" % (self.getLogString(), str(string)))

        if self.focusable:
            if not self.focused:
                try:
                    self.grabFocus()
                except Exception:
                    debug_message(message="Node is focusable but I can't grabFocus!")

            rawinput.typeText(string)

        else:
            debug_message(message="Node is not focusable; falling back to inserting text.")
            et = self.queryEditableText()
            et.insertText(self.caretOffset, string, len(string))
            self.caretOffset += len(string)
            doDelay()


    def keyCombo(self, comboString):
        """
        Press keys in combination.
        """

        debug_message(message="Node.keyCombo - pressing keys: '%s' into '%s'" % (str(comboString), self.getLogString()))

        if self.focusable:
            if not self.focused:
                try:
                    self.grabFocus()
                except Exception:
                    debug_message(message="Node is focusable but I can't grabFocus!")
        else:
            debug_message(message="Node is not focusable; trying key combo anyway.")

        rawinput.keyCombo(comboString)


    def getLogString(self):
        """
        Get a string describing this node for the logs,
        respecting the config.absoluteNodePaths boolean.
        """

        debug_message(message="Node.getLogString - returns a string describing the node for the logs.")

        if config.absoluteNodePaths:
            return self.getAbsoluteSearchPath()
        else:
            return str(self)


    def satisfies(self, pred):
        """
        Does this node satisfy the given predicate?
        """

        debug_message(message="Node.satisfies - does this node satisfy the given predicate? Logic handled by predicate.")

        assert isinstance(pred, predicate.Predicate)
        return pred.satisfiedByNode(self)


    def dump(self, type="plain", fileName=None):
        """
        Dumping a tree structure of the node.
        """

        debug_message(message="Node.dump - dumping a tree structure of the node.")

        from dogtail import dump
        dumper = getattr(dump, type)
        dumper(self, fileName)


    def getAbsoluteSearchPath(self):
        """
        Generate a SearchPath instance giving the 'best'
        way to find the Accessible wrapped by this node again, starting
        at the root and applying each search in turn.

        This is somewhat analagous to an absolute path in a filesystem,
        except that some of searches may be recursive, rather than just
        searching direct children.

        Used by the recording framework for identifying nodes in a
        persistent way, independent of the style of script being
        written.
        """

        debug_message(message="Node.getAbsoluteSearchPath - generates a path to the parent node.")

        if config.debugSearchPaths:
            info_message(message="getAbsoluteSearchPath(%s)" % self)

        if self.roleName == "application":
            result = path.SearchPath()
            result.append(predicate.IsAnApplicationNamed(self.name), False)
            return result

        else:
            if self.parent:
                (ancestor, pred, isRecursive) = self.getRelativeSearch()
                if config.debugSearchPaths:
                    debug_message(message="Found ancestor: %s" % ancestor)

                ancestorPath = ancestor.getAbsoluteSearchPath()
                ancestorPath.append(pred, isRecursive)
                return ancestorPath

            else:
                # This should be the root node:
                return path.SearchPath()


    def getRelativeSearch(self):
        """
        Get a (ancestorNode, predicate, isRecursive) triple that
        identifies the best way to find this Node uniquely.
        """

        debug_message(message="Node.getRelativeSearch - returns a triple of (ancesterNode, pred, isRecursive).")

        if config.debugSearchPaths:
            info_message(message="getRelativeSearchPath(%s)" % self)

        assert self
        assert self.parent

        isRecursive = False
        ancestor = self.parent

        while not self.__nodeIsIdentifiable(ancestor):
            debug_message(message="Node is not identifiable, setting isRecursive as True.")
            ancestor = ancestor.parent
            isRecursive = True

        # I think this is useless, since only change is the debug string

        # Pick the most appropriate predicate for finding this node:
        if self.labellee:
            if self.labellee.name:
                return (ancestor, predicate.IsLabelledAs(self.labellee.name), isRecursive)
        
        if self.roleName == 'menu':
            return (ancestor, predicate.IsAMenuNamed(self.name), isRecursive)
        elif self.roleName == 'menu item' or self.roleName == 'check menu item':
            return (ancestor, predicate.IsAMenuItemNamed(self.name), isRecursive)
        elif self.roleName == 'text':
            return (ancestor, predicate.IsATextEntryNamed(self.name), isRecursive)
        elif self.roleName == 'push button':
            return (ancestor, predicate.IsAButtonNamed(self.name), isRecursive)
        elif self.roleName == 'frame':
            return (ancestor, predicate.IsAWindowNamed(self.name), isRecursive)
        elif self.roleName == 'dialog':
            return (ancestor, predicate.IsADialogNamed(self.name), isRecursive)
        else:
            pred = predicate.GenericPredicate(name=self.name, roleName=self.roleName)
            return (ancestor, pred, isRecursive)


    def __nodeIsIdentifiable(self, ancestor):
        """
        Checks if given node can be identified by labellee, name or parent.
        """

        debug_message(message="Node.__nodeIsIdentifiable - checking if node is identifiable.")

        if ancestor.labellee:
            return True

        elif ancestor.name:
            return True

        elif not ancestor.parent:
            return True

        else:
            return False


    def _fastFindChild(self, pred, recursive=True, showingOnly=None):
        """
        Searches for an Accessible using methods from pyatspi.utils
        """

        debug_message(message="Node._fastFindChild - searching for an Accessible using methods from pyatspi.utils.")

        if isinstance(pred, predicate.Predicate):
            pred = pred.satisfiedByNode

        if showingOnly is None:
            showingOnly = config.searchShowingOnly

        if showingOnly:
            original_predicate = pred
            pred = lambda x: original_predicate(x) and x.getState().contains(pyatspi.STATE_SHOWING)

        if not recursive:
            cIter = iter(self)
            while True:
                try:
                    child = next(cIter)
                except StopIteration:
                    break

                if child is not None and pred(child):
                    return child

        else:
            return pyatspi.utils.findDescendant(self, pred)


    def findChild(self, pred, recursive=True, debugName=None, retry=True, requireResult=True, showingOnly=None):
        """
        Search for a node satisyfing the predicate, returning a Node.

        If retry is True (the default), it makes multiple attempts, backing off and retrying
        on failure, and eventually raises a descriptive exception if the search fails.

        If retry is False, it gives up after one attempt.

        If requireResult is True (the default), an exception is raised after all
        attempts have failed. If it is false, the function simply returns None.
        """

        debug_message(message="Node.findChild - searching for the child of an Accessible.")

        def describeSearch(parent, pred, recursive, debugName):
            """
            Internal helper function
            """

            noun = "descendant" if recursive else "child"

            if debugName is None:
                debugName = pred.describeSearchResult()

            return "%s of %s: %s" % (str(noun), parent.getLogString(), str(debugName))


        compare_function = None
        if isinstance(pred, LambdaType):
            compare_function = pred
            if debugName is None:
                debugName = "child satisyfing a custom lambda function"

        else:
            assert isinstance(pred, predicate.Predicate)
            compare_function = pred.satisfiedByNode

        number_of_attempts = 0
        while number_of_attempts < config.searchCutoffCount:
            if number_of_attempts >= config.searchWarningThreshold or config.debugSearching:
                info_message(message="Searching for '%s' (attempt number: %i)" % \
                    (describeSearch(self, pred, recursive, debugName), number_of_attempts))

            result = self._fastFindChild(compare_function, recursive, showingOnly=showingOnly)

            if result:
                assert isinstance(result, Node)
                if debugName:
                    result.debugName = debugName
                else:
                    result.debugName = pred.describeSearchResult()
                return result

            else:
                if not retry:
                    break
                number_of_attempts += 1
                if config.debugSearching or config.debugSleep:
                    info_message(message="sleeping for '%f'" % config.searchBackoffDuration)
                sleep(config.searchBackoffDuration)

        if requireResult:
            raise SearchError(describeSearch(self, pred, recursive, debugName))


    def findChildren(self, pred, recursive=True, isLambda=False, showingOnly=None):
        """
        Find all children/descendents satisfying the predicate. You can also use lambdas in
        place of the pred that will enable search also against pure dogtail Node properties
        (like showing). I.e: "lambda x: x.roleName == 'menu item' and x.showing is True".
        isLambda does not have to be set, it's kept only for api compatibility.
        """

        debug_message(message="Node.findChildren - searching for the children of an Accessible.")

        compare_function = None
        if isLambda is True or isinstance(pred, LambdaType):
            compare_function = pred

        else:
            assert isinstance(pred, predicate.Predicate)
            compare_function = pred.satisfiedByNode

        if showingOnly is None:
            showingOnly = config.searchShowingOnly

        if showingOnly:
            original_compare_func = compare_function
            compare_function = lambda n: original_compare_func(n) and \
                n.getState().contains(pyatspi.STATE_SHOWING)

        results = []
        number_of_attempts = 0
        while number_of_attempts < config.searchCutoffCount:
            if number_of_attempts >= config.searchWarningThreshold or config.debugSearching:
                info_message(message="Accessibility errors caught, making attempt number: '%f'" % \
                    number_of_attempts)

            try:
                if recursive:
                    results = pyatspi.utils.findAllDescendants(self, compare_function)
                else:
                    results = list(filter(compare_function, self.children))
                break

            except (GLib.GError, TypeError):
                number_of_attempts += 1
                if number_of_attempts == config.searchCutoffCount:
                    info_message(message="Warning: Accessibility errors caught, giving up search.")
                else:
                    sleep(config.searchBackoffDuration)
                continue

        return results


    def findAncestor(self, pred, showingOnly=None):
        """
        Search up the ancestry of this node, returning the first Node
        satisfying the predicate, or None.
        """

        debug_message(message="Node.findAncestor - searching for the Ancestor of an Accessible.")

        assert isinstance(pred, predicate.Predicate)

        candidate = self.parent
        while candidate is not None:
            if candidate.satisfies(pred):
                return candidate
            else:
                candidate = candidate.parent

        return None


    def child(self, name="", roleName="", description="", label="", recursive=True, retry=True, debugName=None, showingOnly=None):
        """
        Finds a child satisying the given criteria.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Node.child - wrapper over findChild using GenericPredicate.")

        return self.findChild(predicate.GenericPredicate(name=name, roleName=roleName, description=description, label=label),
                              recursive=recursive, retry=retry, debugName=debugName, showingOnly=showingOnly)


    def isChild(self, name="", roleName="", description="", label="", recursive=True, retry=False, debugName=None, showingOnly=None):
        """
        Determines whether a child satisying the given criteria exists.

        This is implemented using findChild, but will not automatically retry
        if no such child is found. To make the function retry multiple times set retry to True.
        Returns a boolean value depending on whether the child was eventually found. Similar to
        'child', yet it catches SearchError exception to provide for False results, will raise
        any other exceptions. It also logs the search.
        """

        debug_message(message="Node.isChild - wrapper over findChild using GenericPredicate. \
            Returns bool on search result.")

        try:
            self.findChild(predicate.GenericPredicate(name=name, roleName=roleName, description=description, label=label),
                           recursive=recursive, retry=retry, debugName=debugName, showingOnly=showingOnly)
            return True
        except SearchError:
            return False


    def menu(self, menuName, recursive=True, showingOnly=None):
        """
        Search below this node for a menu with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Node.menu - wrapper over findChild using IsAMenuNamed.")

        return self.findChild(predicate.IsAMenuNamed(menuName=menuName), recursive, showingOnly=showingOnly)


    def menuItem(self, menuItemName, recursive=True, showingOnly=None):
        """
        Search below this node for a menu item with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Node.menuItem - wrapper over findChild using IsAMenuNamed.")

        return self.findChild(predicate.IsAMenuItemNamed(menuItemName=menuItemName), recursive, showingOnly=showingOnly)


    def textentry(self, textEntryName, recursive=True, showingOnly=None):
        """
        Search below this node for a text entry with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Node.textentry - wrapper over findChild using IsATextEntryNamed.")

        return self.findChild(predicate.IsATextEntryNamed(textEntryName=textEntryName), recursive, showingOnly=showingOnly)


    def button(self, buttonName, recursive=True, showingOnly=None):
        """
        Search below this node for a button with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Node.button - wrapper over findChild using IsAButtonNamed.")

        return self.findChild(predicate.IsAButtonNamed(buttonName=buttonName), recursive, showingOnly=showingOnly)


    def childLabelled(self, labelText, recursive=True, showingOnly=None):
        """
        Search below this node for a child labelled with the given text.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Node.childLabelled - wrapper over findChild using IsLabelledAs.")

        return self.findChild(predicate.IsLabelledAs(labelText), recursive, showingOnly=showingOnly)


    def childNamed(self, childName, recursive=True, showingOnly=None):
        """
        Search below this node for a child with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Node.childNamed - wrapper over findChild using IsNamed.")

        return self.findChild(predicate.IsNamed(childName), recursive, showingOnly=showingOnly)


    def tab(self, tabName, recursive=True, showingOnly=None):
        """
        Search below this node for a tab with the given name.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Node.tab - wrapper over findChild using IsATabNamed.")

        return self.findChild(predicate.IsATabNamed(tabName=tabName), recursive, showingOnly=showingOnly)


    def getUserVisibleStrings(self):
        """
        Get all user-visible strings in this node and its descendents.

        (Could be implemented as an attribute)
        """

        debug_message(message="Node.getUserVisibleStrings - returns all visible strings \
            (Node.name, Node.desription) of all Node.children in a list.")

        result = []
        if self.name:
            result.append(self.name)

        if self.description:
            result.append(self.description)

        try:
            children = self.children
        except Exception:
            return result

        for child in children:
            result.extend(child.getUserVisibleStrings())

        return result


    def blink(self):
        """
        Blink will hightlight the current node on the screen. Using Blinker from utility.
        """

        debug_message(message="Node.blink will highlight the node in its position with corresponding size.")

        if not self.extents:
            return False
        else:
            (x, y, w, h) = self.extents
            Blinker(x, y, w, h)
            return True


class LinkAnchor(object):
    """
    Class storing info about an anchor within an Accessibility.Hyperlink, which
    is in turn stored within an Accessibility.Hypertext.
    """

    def __init__(self, node, hypertext, linkIndex, anchorIndex):
        self.node = node
        self.hypertext = hypertext
        self.linkIndex = linkIndex
        self.anchorIndex = anchorIndex


    @property
    def link(self):
        return self.hypertext.getLink(self.linkIndex)


    @property
    def URI(self):
        return self.link.getURI(self.anchorIndex)


class Root(Node):
    """
    Root class used to get data from Accessible.
    """

    def applications(self):
        """
        Get all applications.
        """

        debug_message(message="Root.applications - returns a list of Accessible Application objects.")

        return root.findChildren(predicate.GenericPredicate(roleName="application"), recursive=False, showingOnly=False)


    def application(self, appName, retry=True):
        """
        Gets an application by name, returning an Application instance
        or raising an exception.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Root.application - returns a wanted Accessible Application object.")

        return root.findChild(predicate.IsAnApplicationNamed(appName), recursive=False, retry=retry, showingOnly=False)


class Application(Node):
    """
    Application class used to get data from Accessible.
    """

    def dialog(self, dialogName, recursive=False, showingOnly=None):
        """
        Search below this node for a dialog with the given name,
        returning a Window instance.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Application.dialog - wrapper over findChild using IsADialogNamed.")

        return self.findChild(predicate.IsADialogNamed(dialogName=dialogName), recursive, showingOnly=showingOnly)


    def window(self, windowName, recursive=False, showingOnly=None):
        """
        Search below this node for a window with the given name,
        returning a Window instance.

        This is implemented using findChild, and hence will automatically retry
        if no such child is found, and will eventually raise an exception. It
        also logs the search.
        """

        debug_message(message="Application.window - wrapper over findChild using IsAWindowNamed.")

        result = self.findChild(predicate.IsAWindowNamed(windowName=windowName), recursive, showingOnly=showingOnly)
        return result


    def getWnckApplication(self, showingOnly=None):  # pragma: no cover
        """
        Get the wnck.Application instance for this application, or None

        Currently implemented via a hack: requires the app to have a
        window, and looks up the application of that window

        wnck.Application can give you the pid, the icon, etc
        """

        info_message(message="Application.getWnckApplication - untested.")

        window = self.child(roleName="frame", showingOnly=showingOnly)
        if window:
            wnckWindow = window.getWnckWindow()
            return wnckWindow.get_application()


class Window(Node):
    """
    Window class used to get data from Accessible.
    """

    def getWnckWindow(self):  # pragma: no cover
        """
        Get the wnck.Window instance for this window, or None
        """

        info_message(message="Window.getWnckWindow - untested.")

        screen = Wnck.screen_get_default()
        screen.force_update()
        for wnckWindow in screen.get_windows():
            if wnckWindow.get_name() == self.name:
                return wnckWindow


    def activate(self):  # pragma: no cover
        """
        Activates the wnck.Window associated with this Window.
        """

        info_message(message="Window.activate - untested.")

        wnckWindow = self.getWnckWindow()
        wnckWindow.activate(0)


class Wizard(Window):
    """
    Note that the buttons of a GnomeDruid were not accessible until recent versions of libgnomeui.
    This is http://bugzilla.gnome.org/show_bug.cgi?id=157936 and is fixed in
    gnome-2.10 and gnome-2.12 (in CVS libgnomeui) there's a patch attached to that bug.
    This bug is known to affect FC3; fixed in FC5
    """

    def __init__(self, node, debugName=None):
        Node.__init__(self, node)
        if debugName:
            self.debugName = debugName

        info_message(message="%s is on '%s' page" % (self, self.getPageTitle()))


    def currentPage(self):
        """
        Get the current page of this wizard.
        This is currently a hack, supporting only GnomeDruid
        """

        info_message(message="Wizard.currentPage - untested.")

        pageHolder = self.child(roleName="panel")
        for child in pageHolder.children:
            if child.showing:
                return child

        raise "Unable to determine current page of %s" % self


    def getPageTitle(self):
        """
        Get the string title of the current page of this wizard
        This is currently a total hack, supporting only GnomeDruid
        """

        info_message(message="Wizard.getPageTitle - untested.")

        currentPage = self.currentPage()
        return currentPage.child(roleName="panel").child(roleName="panel").child(roleName="label", recursive=False).text


    def clickForward(self):
        """
        Click on the 'Forward' button to advance to next page of wizard.
        It will log the title of the new page that is reached.
        This will only work if your libgnomeui has accessible buttons see above.
        """

        info_message(message="Wizard.clickForward - untested.")

        fwd = self.child("Forward")
        fwd.click()

        info_message(message="%s is now on '%s' page"% (self, self.getPageTitle()))


    def clickApply(self):
        """
        Click on the 'Apply' button to advance to next page of wizard.
        What if it's Finish rather than Apply?
        This will only work if your libgnomeui has accessible buttons see above.
        """

        info_message(message="Wizard.clickFoclickApplyrward - untested.")

        fwd = self.child("Apply")
        fwd.click()


Accessibility.Accessible.__bases__ = (
    Application, Root, Node,) + Accessibility.Accessible.__bases__


try:
    root = pyatspi.Registry.getDesktop(0)
    root.debugName = "root"
except Exception:  # pragma: no cover
    info_message(message="Error: AT-SPI's desktop is not visible. Is accessibility enabled?")


children = root.children
if not children:  # pragma: no cover
    info_message(message="Warning: AT-SPI's desktop is visible but it has no children. \
        Are you running any AT-SPI-aware applications?")
del children


"""
Sniff also imports from tree and we don't want to run this code from sniff itself.
May have already been locked by dogtail.procedural.
Mark newly opened sniff not to use auto-refresh while script using this module is running.
"""
if not os.path.exists("/tmp/sniff_running.lock") or not os.path.exists("/tmp/sniff_refresh.lock"):
    sniff_lock = Lock(lockname="sniff_refresh.lock", randomize=False, unlockOnExit=True)
    try:
        sniff_lock.lock()
    except OSError:  # pragma: no cover
        pass

elif "sniff" not in sys.argv[0]:
    info_message(message="Dogtail: Warning: Running sniff has been detected.")
    info_message(message="Please make sure sniff has the 'Auto Refresh' disabled.")
#    info_message(message="NOTE: Running scripts with sniff present is not recommended.")
