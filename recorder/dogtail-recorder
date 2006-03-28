#!/usr/bin/env python
__author__ = 'David Malcolm <dmalcolm@redhat.com>, Zack Cerza <zcerza@redhat.com>'

# Event recorder.
# FIXME: under construction
# To quit, click any Edit menu.

import atspi
import dogtail.tree

def logEvent(event):
    source = event.source
    if isinstance(source, atspi.Accessible):
        sourceStr = " source:%s"%(str(dogtail.tree.Node(source)))
    else:
        sourceStr = ""
    print "Got event: %s%s"%(event.type, sourceStr)


class ScriptWriter(Writer):
    """
    Abstract Writer subclass which writes out Python scripts
    """
    def recordClick(self, node):
        raise NotImplementedError

class OOScriptWriter(ScriptWriter):
    """
    Concrete Writer subclass which writes out Python scripts in an object-oriented
    style
    """
    def __init__(self):
        # maintain a dict from variable names to search paths
        self.variables = {}
        self.debug = False
        self.debugVariables = False
        
        print "from dogtail.tree import *"
        print

    def generateVariableName(self, predicate):
        # Ensure uniqueness
        result = predicate.makeScriptVariableName()
        if result in self.variables:
            # This variable name is already in use; need to append a number:
            index = 1
            while result+str(index) in self.variables:
                index+=1
            return result+str(index)
        else:
            return result

    def printVariables(self):
        # debug hook
        print "variables:"
        for (varName, varAbsPath) in self.variables.iteritems():
            print "varName:%s -> absPath:%s"%(varName, varAbsPath)        

    def generateAbsSearchPathMethodCall(self, absSearchPath):
        """
        Generates a method call that identifies the absolute search path,
        optimizing away prefixes where possible with variable names.
        """
        # We optimize away the longest common absolute path prefix, i.e. the
        # shortest relative path suffix:
        if self.debug:
            print "*******************"
            print "generateAbsSearchPathMethodCall for %s"%absSearchPath
            self.printVariables()
            
        shortestRelativePath = None
        for (varName, varAbsPath) in self.variables.iteritems():
            relPath = varAbsPath.getRelativePath(absSearchPath)
            if relPath:
                if shortestRelativePath:
                    if relPath.length() < shortestRelativePath[2].length():
                        shortestRelativePath = (varName, varAbsPath, relPath)
                else:
                    shortestRelativePath = (varName, varAbsPath, relPath)

        if self.debug:
            if shortestRelativePath:
                (varName, varAbsPath, relPath) = shortestRelativePath
                print "shortestRelativePath: (%s, %s, %s)"%(varName, varAbsPath, relPath)
            else:
                print "shortestRelativePath: None"
            print "*******************"

        if shortestRelativePath:
            (varName, varAbsPath, relPath) = shortestRelativePath
            return varName+relPath.makeScriptMethodCall()
        else:
            # Have to specify it as an absolute path:
            return "root"+absSearchPath.makeScriptMethodCall()
    
    def recordKey(self, node, key):
        searchPath = node.getAbsoluteSearchPath()
        result = self.generateAbsSearchPathMethodCall(searchPath)
        result +=".rawType('%s')" % key

    def recordClick(self, node):
        searchPath = node.getAbsoluteSearchPath()

        if self.debug:
            print "----------------------------------"
            print "click on %s"%searchPath
            print "Full script would be: root%s"%searchPath.makeScriptMethodCall()
            
        # Generate variables for nodes likely to be referred to often (application, window)
        # FIXME: make this smarter?
        for i in [1,2,3]:
            if i<searchPath.length():

                prefixPath = searchPath.getPrefix(i)

                if self.debugVariables:
                    print "Considering: %s"%prefixPath

                if not prefixPath in self.variables.values():
                    if self.debugVariables:
                        print "It is not yet a variable"
                        self.printVariables()
                        
                    predicate = prefixPath.getPredicate(i-1)
                    varName = predicate.makeScriptVariableName()
                    print varName+" = "+self.generateAbsSearchPathMethodCall(prefixPath)
                    self.variables[varName]=prefixPath
                else:
                    if self.debugVariables:
                        print "It is already a variable"

        result = self.generateAbsSearchPathMethodCall(searchPath)
        result +=".click()"

        if self.debug:
            print "----------------------------------"

        print result

class ProceduralScriptWriter(ScriptWriter):
    """
    Concrete Writer subclass which writes out Python scripts in a procedural
    style
    """
    def recordClick(self, node):
        # FIXME: not yet written
        raise NotImplementedError

# Singleton EventRecorder
global recorder

class FakeNode(dogtail.tree.Node):
    """A "cached pseudo-copy" of a Node

    This class exists for cases where we know we're going to need information
    about a Node instance at a point in time where it's no longer safe to 
    assume that the Accessible it wraps is still valid. It is designed to 
    cache enough information to allow all of the necessary Node methods to 
    execute properly and return something meaningful.

    As it is often necessary to know the Node instance's parent, it creates 
    FakeNode instances of each and every one of its ancestors.
    """
    def __init__(self, node):
        self.__node = node
        self.name = self.__node.name
        self.roleName = self.__node.roleName
        self.description = self.__node.description
        self.debugName = self.__node.debugName

        try: self.text = self.__node.text
        except AttributeError: self.text = None
        
        try: self.position = self.__node.position
        except AttributeError: self.position = None
        
        try: self.size = self.__node.size
        except AttributeError: self.size = None
        
        if node.parent: self.parent = FakeNode(self.__node.parent)
        else: self.parent = None
        
        if node.labellee: self.labellee = FakeNode(self.__node.labellee)
        else: self.labellee = None

    def __getattr__(self, name):
        raise AttributeError, name

    def __setattr__(self, name, value):
        self.__dict__[name] = value

# Test event recording class; under construction
class EventRecorder:
    def __init__(self):
        self.writer = OOScriptWriter()
        self.listeners = self.__registerEvents()
        self.lastFocusedNode = None
        self.lastSelectedNode = None
        self.lastPressedNode = None
        self.lastReleasedNoed = None
        self.absoluteNodePaths = True
 
    def __registerEvents(self):
        # Only specific events are recorded:
        listeners = []

        # Focus events:
        listeners.append(atspi.EventListener(marshalOnFocus, ["focus:"]))

        # State Changed events:
        listeners.append(atspi.EventListener(marshalOnSelect, ["object:state-changed:selected"]))

        # Mouse button-1 clicks:
        listeners.append(atspi.EventListener(marshalOnMouseButton, ["mouse:button"]))

        # Window creation:
        listeners.append(atspi.EventListener(marshalOnWindowCreate, ["window:create"]))

        return listeners

    def onFocus(self, event): 
        #logEvent(event)
        sourceNode=dogtail.tree.Node(event.source)
        sourceNode = FakeNode(sourceNode)
        self.lastFocusedNode = sourceNode

    def onSelect(self, event):
        #logEvent(event)
        sourceNode = dogtail.tree.Node(event.source)
        sourceNode = FakeNode(sourceNode)
        self.lastSelectedNode = sourceNode
        if sourceNode.name == "Edit":
            atspi.event_quit()

    def onMouseButton(self, event):
        #logEvent(event)
        
        isPress = isRelease = False
        if "mouse:button:1" not in event.type:
            return
        elif event.type == "mouse:button:1p":
            isPress = True
        elif event.type == "mouse:button:1r":
            isRelease = True
        
        # The source node is always "main" - which sucks.
        # sourceNode = dogtail.tree.Node(event.source)

        #print "position", self.lastFocusedNode.position
        #print "size", self.lastFocusedNode.size
        
        x = event.detail1
        y = event.detail2
        #print "x,y: %s, %s" % (x, y)
        for node in (self.lastFocusedNode, self.lastSelectedNode):
            #print "position: %s, size: %s" % (node.position, node.size)
            try:
                if node.position:
                    if node.position[0] <= x <= (node.position[0] + node.size[0]) and \
                            node.position[1] <= y <= (node.position[1] + node.size[1]):
                        if isPress: self.lastPressedNode = node
                        elif isRelease: self.lastReleasedNode = node
                        break
            except AttributeError: pass
        
        if isRelease: self.writer.recordClick(self.lastFocusedNode)

    def onWindowCreate(self, event):
        # logEvent(event)
        sourceNode = dogtail.tree.Node(event.source)
        # print "Window creation: %s"%str(sourceNode)

    def getLogStringForNode(self, node):
        if self.absoluteNodePaths:
            return node.getAbsoluteSearchPath()
        else:
            return node
    
# Under construction.  These ought to be methods, but am having Python assertion
# failures in refcounting when trying to hook them up using lambda expressions; grrr...
def marshalOnFocus(event): 
    recorder.onFocus(event)

def marshalOnSelect(event):
    recorder.onSelect(event)

def marshalOnMouseButton(event):
    recorder.onMouseButton(event)

def marshalOnWindowCreate(event): 
    recorder.onWindowCreate(event)

recorder = EventRecorder()
#recorder.writer.debug = True
#recorder.writer.debugVariables = True
atspi.event_main()

# vim: sw=4 ts=4 sts=4 et ai
