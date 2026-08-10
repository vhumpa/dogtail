#!/usr/bin/python3
"""
GUI test tool and automation framework that uses Accessibility (a11y) technologies
to communicate with desktop applications.
"""

# ruff: noqa: BLE001

__author__ = """
Michal Odehnal <modehnal@redhat.com>,
Vita Humpa <vhumpa@redhat.com>,
Zack Cerza <zcerza@redhat.com>,
Ed Rousseau <rousseau@redhat.com>,
David Malcolm <dmalcolm@redhat.com>,
"""

try:
    from ._version import __version__ as imported_version
    __version__ = imported_version
except Exception:
    __version__ = "Unavailable"

__url__ = "https://gitlab.com/dogtail/dogtail"
__copyright__ = "Copyright © 2005-2026 Red Hat, Inc."
__license__ = "GPLv2"
__all__ = (
    "config",
    "distro",
    "dump",
    "errors",
    "logging",
    "ponytail_helper",
    "predicate",
    "rawinput",
    "tree",
    "utils",
    "version",
)
