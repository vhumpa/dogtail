"""Utility functions for 'dumping' trees of Node objects.

Author: Zack Cerza <zcerza@redhat.com>"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

# Just exit on ^C. Maybe something less drastic should happen, though...
# Anyway, I'd *love* to be able to unregister this signal handler.
import signal, sys
def signalHandler (signal, frame):
	sys.exit(0)
signal.signal(signal.SIGINT, signalHandler)

spacer = ' '
def plain (node, depth = 0):
	"""
	Plain-text dump. The hierarchy is represented through indentation.
	The default indentation string is a single space, ' ', but can be changed.
	"""
	print spacer*(depth) + str (node)
	try:
		for action in node.actions:
			print spacer*(depth + 1) + str (action)
	except AttributeError: pass
	try:
		for child in node.children:
			plain (child, depth + 1)
	except AttributeError: pass

def xml (node):
	try: import cElementTree as ElementTree
	except ImportError: from elementtree import ElementTree
	def buildElementTree (parentElement, node):
		element = ElementTree.SubElement(parentElement, 'node')
		name = ElementTree.SubElement(element, 'name')
		name.text = node.name
		roleName = ElementTree.SubElement(element, 'roleName')
		roleName.text = node.roleName
		description = ElementTree.SubElement(element, 'description')
		description.text = node.description
		try:
			text = ElementTree.SubElement(element, 'text')
			text.text = node.text
		except AttributeError: pass
		
		try:
			for action in node.actions:
				actionElement = ElementTree.SubElement(element, 'action')
				name = ElementTree.SubElement(actionElement, 'name')
				name.text = action.name
				description = ElementTree.SubElement(actionElement, 'description')
				description.text = action.description
				keyBinding = ElementTree.SubElement(actionElement, 'keyBinding')
				keyBinding.text = action.keyBinding
		except AttributeError: pass	
		
		try:
			for child in node.children:
				buildElementTree(element, child)
		except AttributeError: pass
	root = ElementTree.Element('node')
	element = root
	buildElementTree(root, node)
	tree = ElementTree.ElementTree(root)
	ElementTree.dump(tree)
		

