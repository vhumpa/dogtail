#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
Handles General exceptions, not overly module-specific.
"""

# pylint: disable=line-too-long
# ruff: noqa: E501

import inspect

from dogtail.logging import logging_class
LOGGING = logging_class.logger

__author__ = "Zack Cerza <zcerza@redhat.com>"


def warn(message, caller=True):
    """
    Generate a warning, and pass it to the debug logger.
    """

    last_frame_info_object = inspect.stack()[-1]

    # frame = last_frame_info_object[0]
    file_name = last_frame_info_object[1]
    lineno = last_frame_info_object[2]
    #function = last_frame_info_object[3]
    code_context = last_frame_info_object[4]
    # index = last_frame_info_object[5]

    new_message = f"Warning: {file_name}:{lineno}: {message}"
    if caller and file_name != "<stdin>" and file_name != "<string>" and code_context:
        new_message = new_message + ":\n  " + code_context[0]
    del last_frame_info_object

    LOGGING.debug(new_message)


class DependencyNotFoundError(Exception):
    """
    A dependency was not found.
    """
