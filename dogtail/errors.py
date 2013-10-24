# -*- coding: utf-8 -*-
"""
General exceptions; not overly module-specific
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"
from logging import debugLogger as logger

import inspect


def warn(message, caller=True):
    """
    Generate a warning, and pass it to the debug logger.
    """
    frameRec = inspect.stack()[-1]
    message = "Warning: %s:%s: %s" % (frameRec[1], frameRec[2], message)
    if caller and frameRec[1] != '<stdin>' and frameRec[1] != '<string>':
        message = message + ':\n  ' + frameRec[4][0]
    del frameRec
    logger.log(message)


class DependencyNotFoundError(Exception):

    """
    A dependency was not found.
    """
    pass
