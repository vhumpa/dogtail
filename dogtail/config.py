# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import locale
import os
import sys
import pwd
import json

"""
The configuration module.
"""

__author__ = """
Zack Cerza <zcerza@redhat.com>,
David Malcolm <dmalcolm@redhat.com>
"""


def _userTmpDir(baseName):
    # i.e. /tmp/dogtail-foo
    logname = os.getenv("LOGNAME", default=pwd.getpwuid(os.getuid())[0])
    return "-".join(("/".join(("/tmp", baseName)), logname))


class _Config:

    """
    Contains configuration parameters for the dogtail run.

    scratchDir(str):
    Directory where things like screenshots are stored.

    dataDir(str):
    Directory where related data files are located.

    logDir(str):
    Directory where dogtail.tc.TC*-generated logs are stored.

    scriptName(str) [Read-Only]:
    The name of the script being run.

    encoding(str)
    The encoding for text, used by dogtail.tc.TCString .

    actionDelay(float):
    The delay after an action is executed.

    typingDelay(float):
    The delay after a character is typed on the keyboard.

    runInterval(float):
    The interval at which dogtail.utils.run() and dogtail.procedural.run()
    check to see if the application has started up.

    runTimeout(int):
    The timeout after which dogtail.utils.run() and dogtail.procedural.run()
    give up on looking for the newly-started application.

    searchBackoffDuration (float):
    Time in seconds for which to delay when a search fails.

    searchWarningThreshold (int):
    Number of retries before logging the individual attempts at a search.

    searchCutoffCount (int):
    Number of times to retry when a search fails.

    searchShowingOnly (boolean):
    Whether to only search among nodes that are currently being shown.

    defaultDelay (float):
    Default time in seconds to sleep when delaying.

    childrenLimit (int):
    When there are a very large number of children of a node, only return
    this many, starting with the first.

    debugSearching (boolean):
    Whether to write info on search backoff and retry to the debug log.

    debugSleep (boolean):
    Whether to log whenever we sleep to the debug log.

    debugSearchPaths (boolean):
    Whether we should write out debug info when running the SearchPath
    routines.

    absoluteNodePaths (boolean):
    Whether we should identify nodes in the logs with long 'abcolute paths', or
    merely with a short 'relative path'.

    ensureSensitivity (boolean):
    Should we check that ui nodes are sensitive (not 'greyed out') before
    performing actions on them? If this is True (the default) it will raise
    an exception if this happens. Can set to False as a workaround for apps
    and toolkits that don't report sensitivity properly.

    debugTranslation (boolean):
    Whether we should write out debug information from the translation/i18n
    subsystem.

    blinkOnActions (boolean):
    Whether we should blink a rectangle around a Node when an action is
    performed on it.

    fatalErrors (boolean):
    Whether errors encountered in dogtail.procedural should be considered
    fatal. If True, exceptions will be raised. If False, warnings will be
    passed to the debug logger.

    checkForA11y (boolean):
    Whether to check if accessibility is enabled. If not, just assume it is
    (default True).

    buttonRoleCompat (boolean):
    Whether to convert "button" role names to "push button" for backwards
    compatibility (default False).

    logDebugToFile (boolean):
    Whether to write debug output to a log file.

    logDebugToStdOut (boolean):
    Whether to print log output to console or not (default True).
    """

    @property
    def scriptName(self):
        return os.path.basename(sys.argv[0]).replace(".py", "")


    @property
    def encoding(self):
        return locale.getpreferredencoding().lower()


    defaults = {
        # Storage
        "scratchDir": '/'.join((_userTmpDir("dogtail"), "")),
        "dataDir": '/'.join((_userTmpDir("dogtail"), "data", "")),
        "logDir": '/'.join((_userTmpDir("dogtail"), "logs", "")),
        "scriptName": scriptName.fget(None),
        "encoding": encoding.fget(None),
        "configFile": None,
        "baseFile": None,

        # Timing and Limits
        "actionDelay": 1.0,
        "typingDelay": 0.1,
        "runInterval": 0.5,
        "runTimeout": 30,
        "doubleClickDelay": 0.1,
        "searchBackoffDuration": 0.5,
        "searchWarningThreshold": 3,
        "searchCutoffCount": 20,
        "searchShowingOnly": False,
        "defaultDelay": 0.5,
        "childrenLimit": 100,
        "gtk4Offset": (12, 12), # offset to add to ui element position with shadows DISABLED (bigger and variable offset present otherwise, disable shadows!)

        # Debug
        "debugSearching": False,
        "debugSleep": False,
        "debugSearchPaths": False,
        "logDebugToStdOut": True,
        "absoluteNodePaths": False,
        "ensureSensitivity": False,
        "debugTranslation": False,
        "blinkOnActions": False,
        "fatalErrors": False,
        "checkForA11y": True,
        "buttonRoleCompat": False,

        # Logging
        "logDebugToFile": True
    }

    options = {}

    invalidValue = "__INVALID__"


    def __init__(self):
        self.__createDir(self.defaults["scratchDir"])
        self.__createDir(self.defaults["logDir"])
        self.__createDir(self.defaults["dataDir"])
        # Load system-wide configuration files
        self.__loadSystemConfig()


    def __setattr__(self, name, value):
        if name not in config.defaults:
            raise AttributeError(name + " is not a valid option.")

        if self.defaults[name] != value or \
                self.options.get(name, self.invalidValue) != value:
            if "Dir" in name:
                self.__createDir(value)
                value = value.rstrip("/") + os.path.sep

            elif name == "logDebugToFile":
                from dogtail import logging
                logging.debugLogger = logging.Logger("debug", value)

            self.options[name] = value


    def __getattr__(self, name):
        try:
            return self.options[name]
        except KeyError:
            try:
                return self.defaults[name]
            except KeyError:
                raise AttributeError("%s is not a valid option." % name)


    @classmethod
    def __createDir(cls, dirName, perms=0o777):
        """
        Creates a directory (if it doesn't currently exist), creating any
        parent directories it needs.

        If perms is None, create with python's default permissions.
        """

        dirName = os.path.abspath(dirName)

        if not os.path.isdir(dirName):
            umask = os.umask(0)
            os.makedirs(dirName, perms)
            os.umask(umask)

    def __loadSystemConfig(self):
        """
        Loads system-wide configuration files from standard locations.
        Checks for config files in this order:
        1. /etc/dogtail/config
        2. /etc/dogtail/config.json
        """
        config_paths = [
            "/etc/dogtail/config",
            "/etc/dogtail/config.json"
        ]
        
        for config_path in config_paths:
            if os.path.isfile(config_path):
                try:
                    self.__loadConfigFile(config_path)
                    break  # Only load the first config file found
                except Exception:
                    # Silently continue if config file can't be loaded
                    continue

    def __loadConfigFile(self, config_path):
        """
        Loads configuration from a file.
        Supports both JSON format and simple key=value format.
        """
        with open(config_path, 'r') as f:
            content = f.read().strip()
            
        if config_path.endswith('.json'):
            # JSON format
            config_data = json.loads(content)
        else:
            # Simple key=value format
            config_data = {}
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Convert boolean strings
                        if value.lower() in ('true', 'yes', '1'):
                            value = True
                        elif value.lower() in ('false', 'no', '0'):
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        elif value.replace('.', '', 1).isdigit():
                            value = float(value)
                        
                        config_data[key] = value
        
        # Only load valid config options
        valid_config = {k: v for k, v in config_data.items() if k in self.defaults}
        if valid_config:
            self.load(valid_config)


    def load(self, dictt):
        """
        Loads values from dict, preserving any options already set that are not overridden.
        """

        self.options.update(dictt)


    def reset(self):
        """
        Resets all settings to their defaults.
        """

        _Config.options = {}


config = _Config()
