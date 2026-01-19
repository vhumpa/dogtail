#!/usr/bin/python3
"""
GUI test tool and automation framework that uses Accessibility (a11y) technologies
to communicate with desktop applications.
"""

from ._version import __version__

__author__ = """Zack Cerza <zcerza@redhat.com>,
Ed Rousseau <rousseau@redhat.com>,
David Malcolm <dmalcolm@redhat.com>,
Vita Humpa <vhumpa@redhat.com>,
Michal Odehnal <modehnal@redhat.com>
"""

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
