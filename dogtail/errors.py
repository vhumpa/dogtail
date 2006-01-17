# -*- coding: <utf-8> -*-
"""
General exceptions; not overly module-specific
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"


class DependencyNotFoundError(Exception):
	"""
	A dependency was not found.
	"""
	pass

