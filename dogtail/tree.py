#!/usr/bin/env python
"""Makes some sense of the AT-SPI API

The tree API handles various things for you:
- fixes most timing issues
- can automatically generate (hopefully) highly-readable logs of what the
script is doing
- traps various UI malfunctions, raising exceptions for them (again,
hopefully improving the logs)

The most important class is Node.  Each Node is an element of the desktop UI.
There is a tree of nodes, starting at 'root', with applications as its
children, with the top-level windows and dialogs as their children.  The various
widgets that make up the UI appear as descendents in this tree.  All of these
elements (root, the applications, the windows, and the widgets) are represented
as instances of Node in a tree (provided that the program of interest is
correctly exporting its user-interface to the accessibility system).  The Node
class is a wrapper around Accessible and the various Accessible interfaces.

The Action class represents an action that the accessibility layer exports as
performable on a specific node, such as clicking on it.  It's a wrapper around
AccessibleAction.

We often want to look for a node, based on some criteria, and this is provided
by the Predicate class.

Dogtail implements a high-level searching system, for finding a node (or
nodes) satisfying whatever criteria you are interested in.	It does this with
a 'backoff and retry' algorithm. This fixes most timing problems e.g. when a
dialog is in the process of opening but hasn't yet done so.

If a search fails, it waits 'config.searchBackoffDuration' seconds, and then
tries again, repeatedly.  After several failed attempts (determined by
config.searchWarningThreshold) it will start sending warnings about the search
to the debug log.  If it still can't succeed after 'config.searchCutoffCount'
attempts, it raises an exception containing details of the search. You can see
all of this process in the debug log by setting 'config.debugSearching' to True

We also automatically add a short delay after each action
('config.defaultDelay' gives the time in seconds).	We'd hoped that the search
backoff and retry code would eliminate the need for this, but unfortunately we
still run into timing issues.	 For example, Evolution (and probably most
other apps) set things up on new dialogs and wizard pages as they appear, and
we can run into 'setting wars' where the app resets the widgetry to defaults
after our script has already filled out the desired values, and so we lose our
values.  So we give the app time to set the widgetry up before the rest of the
script runs.

The classes trap various UI malfunctions and raise exceptions that better
describe what went wrong.  For example, they detects attempts to click on an
insensitive UI element and raise a specific exception for this.

Unfortunately, some applications do not set up the 'sensitive' state
correctly on their buttons (e.g. Epiphany on form buttons in a web page).  The
current workaround for this is to set config.ensureSensitivity=False, which
disables the sensitivity testing. 

Authors: Zack Cerza <zcerza@redhat.com>, David Malcolm <dmalcolm@redhat.com>
"""
__author__ = """Zack Cerza <zcerza@redhat.com>,
David Malcolm <dmalcolm@redhat.com>
"""

import re
import predicate
from datetime import datetime
from time import sleep
from config import config
from utils import doDelay
from utils import Blinker
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
	print "Warning: Dogtail could not import the Python bindings for libwnck.  Window-manager manipulation will not be available."
	gotWnck = False

SearchError = "Couldn't find"

class NotSensitiveError(Exception):
	"""
	The widget is not sensitive.
	"""
	message = "Cannot %s %s. It is not sensitive."
	def __init__(self, action):
		self.action = action
	
	def __str__(self):
		return self.message % (self.action.name, self.action.node.getLogString())

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
		
		This function is wired in automatically for each of 'Node.click()',
		'Node.press()' etc for every action exported on that node's
		Accessible by Node.__getattr__
		"""
		assert isinstance(self, Action)
		logger.log("%s on %s"%(self.name, self.node.getLogString()))
		if not self.node.sensitive:
			if config.ensureSensitivity:
				raise NotSensitiveError, self
			else:
				nSE = NotSensitiveError(self)
				print "Warning: " + str(nSE)
		result = self.__action.doAction (self.__index)
		doDelay()
		return result

class Node:
	"""
	A node in the tree of UI elements. It wraps an Accessible and
	exposes its useful members.  It also has a debugName which is set
	up automatically when doing searches.

	Node instances have various attributes synthesized, to make it easy to
	get and the underlying accessible data.  Many more attributes can be
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
	A Node instance wrapping the parent, or None.  Wraps Accessible_getParent

	'children' (read-only list of Node instances):
	The children of this node, wrapping getChildCount and getChildAtIndex 

	'text' (string):
	For instances wrapping AccessibleText, the text.  This is read-only,
	unless the instance wraps an AccessibleEditableText.  In this case, you
	can write values to the attribute.  This will get logged in the debug
	log, and a delay will be added.  After the delay, the content of the
	node will be checked to ensure that it has the expected value.  If it
	does not, an exception will be raised.  This does not work for password
	dialogs (since all we get back are * characters).  In this case, set
	the passwordText attribute instead.

	'passwordText' (write-only string):
	See documentation of 'text' attribute above.
	
	'caretOffset' (read/write int):
	For instances wrapping AccessibleText, the location of the text caret,
	expressed as an offset in characters.

	'combovalue' (write-only string):
	For comboboxes.  Write to this attribute to set the combobox to the
	given value, with appropriate delays and logging.

	'stateSet' (read-only StateSet instance):
	Wraps Accessible_getStateSet; a set of boolean state flags
	
	'relations' (read-only list of atspi.Relation instances):
	Wraps Accessible_getRelationSet

	'labellee' (read-only list of Node instances):
	The node(s) that this node is a label for.  Generated from 'relations'.

	'labeller' (read-only list of Node instances):
	The node(s) that is/are a label for this node.  Generated from
	'relations'.

	'sensitive' (read-only boolean):
	Is this node sensitive (i.e. not greyed out).  Generated from stateSet
	based on presence of atspi.SPI_STATE_SENSITIVE
	Not all applications/toolkits seem to properly set this up.

	'showing' (read-only boolean):
	Generated from stateSet based on presence of atspi.SPI_STATE_SHOWING

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
	contained = ('__accessible', '__action', '__component', '__text', '__editableText')

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
		action = self.__accessible.getAction()
		if action is not None:
			self.__action = action

		# Swallow the Component object, if it exists
		component = self.__accessible.getComponent()
		if component is not None:
			self.__component = component
			
			def grabFocus():
				self.__component.grabFocus()
			self.grabFocus = grabFocus

			def rawClick(button = 1):
				"""
				Generates a raw mouse click event whether or not the Node has a 'click' action, using the specified button.
				1 is left,
				2 is middle,
				3 is right.
				"""
				import rawinput
				extents = self.extents
				position = (extents[0], extents[1])
				size = (extents[2], extents[3])
				clickX = position[0] + 0.5 * size[0]
				clickY = position[1] + 0.5 * size[1]
				if config.debugSearching: logger.log("raw click on %s %s at (%s,%s)"%(self.name, self.getLogString(), str(clickX), str(clickY)))
				rawinput.click(clickX, clickY, button)
			self.rawClick = rawClick

			def rawType(text):
				"""
				Generates raw keyboard events to type text into the Node.
				"""
				import rawinput
				if config.debugSearching: logger.log("Typing text '%s' into %s"%(text, self.getLogString()))
				self.grabFocus()
				rawinput.typeText(text)
			self.rawType = rawType
			
		# Swallow the Text object, if it exists
		text = self.__accessible.getText()
		if text is not None: 
			self.__text = text
			self.addSelection = self.__text.addSelection
			self.getNSelections = self.__text.getNSelections
			self.removeSelection = self.__text.removeSelection
			self.setSelection = self.__text.setSelection

		# Swallow the EditableText object, if it exists
		editableText = self.__accessible.getEditableText()
		if editableText is not None:
			self.__editableText = editableText
			self.setAttributes = self.__editableText.setAttributes

		# Swallow the Hypertext object, if it exists
		hypertext = self.__accessible.getHypertext()
		if hypertext is not None:
			self.__hypertext = hypertext

		# Add more objects here. Nobody uses them yet, so I haven't.
		# You also need to change the __getattr__ and __setattr__ functions.

	# It'd be nice to know if two objects are "identical". However, the
	# approach below does not work, since atspi.Accessible doesn't know
	# how to check if two cspi.Accessible objects are "identical" either. :(
	#def __cmp__ (self, node):
	#	 return self.__accessible == node.__accessible

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
			try:
				parentAcc = self.__accessible.getParent ()
				if parentAcc:
					parent = Node (parentAcc)
					return parent
				else:
					return None
			except AttributeError:
				# Wrap the AttributeError to be more informative.
				raise AttributeError, attr
		elif attr == "children":
			if self.__hideChildren: raise AttributeError, attr
			children = []
			for i in xrange (self.__accessible.getChildCount ()):
				children.append (Node (self.__accessible.getChildAtIndex (i)))
			# Attributes from the Hypertext object
			try:
				for i in range(self.__hypertext.getNLinks()):
					children.append(Link(self, self.__hypertext.getLink(i), i))
			except AttributeError: pass
			if children: return children
			else:
				raise AttributeError, attr
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
		
		# Attributes from the Action object
		elif attr == "actions":
			actions = []
			for i in xrange (self.__action.getNActions ()):
				actions.append (Action (self, self.__action, i))
			if actions: 
				return actions
			else:
				raise AttributeError, attr
		elif attr in Action.types:
			# synthesize a function named after each Action supported by this Node (e.g. "click"):
			actions = self.actions
			for action in actions:
				# action.do() is a function that, when called, executes the AT-SPI
				# action associated with the Action instance. Here, we're simply
				# returning a copy of the function, with a different name.
				if action.name == attr: return action.do
			raise AttributeError, attr

		# Attributes from the Component object
		elif attr == "extents":
			return self.__component.getExtents ()
		elif attr == "position":
			return self.__component.getPosition ()
		elif attr == "size":
			return self.__component.getSize ()

		# Attributes from the Text object
		elif attr == "text":
			return self.__text.getText (0, 32767)
		elif attr == "caretOffset":
			return self.__text.getCaretOffset ()

		# Attributes from the Component object
		elif attr == "extents":
			return self.__component.getExtents ()

		else: raise AttributeError, attr

	def __setattr__ (self, attr, value):
		if False: pass
		
		# Are we swallowing an AT-SPI object?
		elif attr.replace('_Node', '') in self.contained:
			self.__dict__[attr] = value

		# Attributes from the Text object
		elif attr=="caretOffset":
			self.__text.setCaretOffset(value)

		# Attributes from the EditableText object
		elif attr=="text":
			"""
			Set the text of the node to the given value, with
			appropriate delays and logging, then test the result:
			"""
			if config.debugSearching: logger.log("Setting text of %s to '%s'"%(self.getLogString(), value))
			self.__editableText.setTextContents (value)
			doDelay()

			#resultText = self.text
			#if resultText != value:
			#	raise "%s failed to have its text set to '%s'; value is '%s'"%(self.getLogString(), value, resultText)

		elif attr=='passwordText':
			"""
			Set the text of the node to the given value, with
			appropriate delays and logging.  We can't test the
			result, we'd only get * characters back.
			"""
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

		FIXME: Doesn't work well at the moment
		"""
		logger.log("Typing text into %s: '%s'"%(self.getLogString(), string))

		# Non-working implementation
		# Unfortunately, the call to AccessibleText_setCaretOffset fails for Evolution's gtkhtml composer for some reason		
		if False:
			print "caret offset: %s"%self.caretOffset
			self.__editableText.insertText (self.caretOffset, text)
			self.caretOffset+=len(string) # FIXME: is this correct?
			print "new caret offset: %s"%self.caretOffset

		# Another non-working implementation
		# Focus the node and inject and keyboard event:
		# Unfortunately, this doesn't work well with Evolution either
		if False:
			self.grabFocus()
			doDelay()
			ev = atspi.EventGenerator()
			ev.injectKeyboardString (string)

		# This approach partially works:
		if True:
			self.text += string
		
		doDelay()

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
			try: string = string + " roleName='%s'" % self.roleName
			except AttributeError: pass
			string = string + " name='%s' description='%s'" % (self.name, self.description)
			try: string = string + " text='%s'" % self.text
			except AttributeError: pass
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
			print "getAbsoluteSearchPath(%s)"%self
			
		if self.roleName=='application':
			result =path.SearchPath()
			result.append(predicate.IsAnApplicationNamed(self.name), False)
			return result
		else:
			if self.parent:
				(ancestor, pred, isRecursive) = self.getRelativeSearch()
				if config.debugSearchPaths:
					print "got ancestor: %s"%ancestor
				
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
			print "getRelativeSearchPath(%s)"%self
			
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

	def grabFocus(self):
		return self.__component.grabFocus ()

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
				print "searching for %s (attempt %i)"%(describeSearch(self, pred, recursive, debugName), numAttempts)
			
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
					print "sleeping for %f"%config.searchBackoffDuration
				sleep(config.searchBackoffDuration)
		if requireResult:
			raise SearchError, describeSearch(self, pred, recursive, debugName)

	# The canonical "search for multiple" method:
	def findChildren(self, pred, recursive = True):
		"""
		Find all children/descendents satisfying the predicate.
		"""
		assert isinstance(pred, predicate.Predicate)

		selfList = []

		try: children = self.children
		except: return None

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
		try:
			(x, y, w, h) = self.extents
			blinkData = Blinker(x, y, w, h, count)
			return True
		except AttributeError:
			return False

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
				raise AttributeError, name
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
		if no such child is found, and will eventually raise an exception.  It
		also logs the search.
		"""
		return Application(root.findChild(predicate.IsAnApplicationNamed(appName),recursive=False))

class Application (Node):
	def dialog(self, dialogName, recursive=False):
		"""
		Search below this node for a dialog with the given name,
		returning a Window instance.

		This is implemented using findChild, and hence will automatically retry
		if no such child is found, and will eventually raise an exception.  It
		also logs the search.
		
		FIXME: should this method activate the dialog?
		"""
		return self.findChild(predicate.IsADialogNamed(dialogName=dialogName), recursive)

	def window(self, windowName, recursive=False):
		"""
		Search below this node for a window with the given name,
		returning a Window instance.

		This is implemented using findChild, and hence will automatically retry
		if no such child is found, and will eventually raise an exception.  It
		also logs the search.		

		FIXME: this bit isn't true:
		The window will be automatically activated (raised and focused
		by the window manager) if wnck bindings are available.
		"""
		result = Window(self.findChild (predicate.IsAWindowNamed(windowName=windowName), recursive))
		# FIXME: activate the WnckWindow ?
		#if gotWnck:
		#	result.activate()
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
	recent versions of libgnomeui.	This is
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
	print "Error: AT-SPI's desktop is not visible. Do you have accessibility enabled?"

try:
	# Check that there are applications running. Warn if none are.
	test = root.children
	del test
except AttributeError:
	print "Warning: AT-SPI's desktop is visible but it has no children. Are you running any AT-SPI-aware applications?"

# This is my poor excuse for a unit test.
if __name__ == '__main__':
	import tc
	f=root.findChild(name="File", roleName="menu")
	case = tc.TCNumber()
	case.compare("File menu text", 4, len(f.text), "float")
	print case.result

# Convenient place to set some debug variables:
#config.debugSearching = True
#config.absoluteNodePaths = True
