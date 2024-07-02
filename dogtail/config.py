
#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

import configparser

# TODO might be worth keeping getters and setters to the dictionary.

# TODO add backwards compatibility for camelCasing

# Make sure it works as https://gitlab.com/dogtail/dogtail/-/issues/12

class _Config:
    """
    Config class to keep backwards compatibility and to have getters and setters.
    """

    # Create a ConfigParser object.
    _config = configparser.ConfigParser()

    # Read the configuration file.
    # TODO Figure out where the file will be.
    _config.read("config.ini")

    NO_VALUES = ["", "n", "no", "f", "false", "False", "0"]

    # Access values from the configuration file.
    # Timing Delay section.
    section = "TimingDelay"
    action_delay = float(_config.get(section, "action_delay", fallback=1.0))
    typing_delay = float(_config.get(section, "typing_delay"))
    default_delay = float(_config.get(section, "default_delay"))
    double_click_delay = float(_config.get(section, "double_click_delay"))
    search_back_off_delay = float(_config.get(section, "search_back_off_delay"))

    # Searching section.
    section = "Searching"
    search_warning_threshold = int(_config.get(section, "search_warning_threshold"))
    search_cut_off_limit = int(_config.get(section, "search_cut_off_limit"))
    search_showing_only = _config.get(section, "search_showing_only") not in NO_VALUES

    # Children Limit section.
    section = "ChildrenLimit"
    children_limit = _config.get(section, "children_limit")

    # Util Scripts section.
    section = "UtilScripts"
    run_interval = _config.get(section, "run_interval")
    run_timeout = _config.get(section, "run_timeout")

    # GTK4Offset section.
    section = "GTK4Offset"
    offset = _config.get(section, "offset")

    # Debug section.
    section = "Debug"
    debug_dogtail = _config.get(section, "debug_dogtail") not in NO_VALUES
    debug_searching = _config.get(section, "debug_searching") not in NO_VALUES
    debug_sleep = _config.get(section, "debug_sleep") not in NO_VALUES
    debug_search_paths = _config.get(section, "debug_search_paths") not in NO_VALUES

    # Debug section.
    section = "Setting"
    log_to_std_out = _config.get(section, "log_to_std_out") not in NO_VALUES
    absolute_node_paths = _config.get(section, "absolute_node_paths") not in NO_VALUES
    ensure_sensitivity = _config.get(section, "ensure_sensitivity") not in NO_VALUES
    fatal_errors = _config.get(section, "fatal_errors") not in NO_VALUES
    check_for_a11y = _config.get(section, "check_for_a11y") not in NO_VALUES

    # Debug section.
    section = "CompatibilityTOREMOVE"
    scratchDir = _config.get(section, "scratchDir", fallback="")
    dataDir = _config.get(section, "dataDir", fallback="")
    logDir = _config.get(section, "logDir", fallback="")
    scriptName = _config.get(section, "scriptName", fallback="")
    encoding = _config.get(section, "encoding", fallback="")
    configFile = _config.get(section, "configFile", fallback="")
    baseFile = _config.get(section, "baseFile", fallback="")
    actionDelay = _config.get(section, "actionDelay", fallback=1.0)
    typingDelay = _config.get(section, "typingDelay", fallback=0.1)
    runInterval = _config.get(section, "runInterval", fallback=0.5)
    runTimeout = _config.get(section, "runTimeout", fallback=30)
    doubleClickDelay = _config.get(section, "doubleClickDelay", fallback=0.1)
    searchBackoffDuration = _config.get(section, "searchBackoffDuration", fallback=0.5)
    searchWarningThreshold = _config.get(section, "searchWarningThreshold", fallback=3)
    searchCutoffCount = _config.get(section, "searchCutoffCount", fallback=20)
    searchShowingOnly = _config.get(section, "searchShowingOnly", fallback=False)
    defaultDelay = _config.get(section, "defaultDelay", fallback=0.5)
    childrenLimit = _config.get(section, "childrenLimit", fallback=100)
    gtk4Offset = _config.get(section, "gtk4Offset", fallback=(12, 12))
    debugSearching = _config.get(section, "debugSearching", fallback=False)
    debugSleep = _config.get(section, "debugSleep", fallback=False)
    debugSearchPaths = _config.get(section, "debugSearchPaths", fallback=False)
    logDebugToStdOut = _config.get(section, "logDebugToStdOut", fallback=True)
    absoluteNodePaths = _config.get(section, "absoluteNodePaths", fallback=False)
    ensureSensitivity = _config.get(section, "ensureSensitivity", fallback=False)
    debugTranslation = _config.get(section, "debugTranslation", fallback=False)
    blinkOnActions = _config.get(section, "blinkOnActions", fallback=False)
    fatalErrors = _config.get(section, "fatalErrors", fallback=False)
    checkForA11y = _config.get(section, "checkForA11y", fallback=True)
    logDebugToFile = _config.get(section, "logDebugToFile", fallback=True)

    ###

    # Return a dictionary with the retrieved values
    options = {
        "action_delay": action_delay,
        "typing_delay": typing_delay,
        "default_delay": default_delay,
        "double_click_delay": double_click_delay,
        "search_back_off_delay": search_back_off_delay,
        "search_warning_threshold": search_warning_threshold,
        "search_cut_off_limit": search_cut_off_limit,
        "search_showing_only": search_showing_only,
        "children_limit": children_limit,
        "run_interval": run_interval,
        "run_timeout": run_timeout,
        "offset": offset,
        "debug_dogtail": debug_dogtail,
        "debug_searching": debug_searching,
        "debug_sleep": debug_sleep,
        "debug_search_paths": debug_search_paths,
        "log_to_std_out": log_to_std_out,
        "absolute_node_paths": absolute_node_paths,
        "ensure_sensitivity": ensure_sensitivity,
        "fatal_errors": fatal_errors,
        "check_for_a11y": check_for_a11y,

        # TODO remove
        "scratchDir": scratchDir,
        "dataDir": dataDir,
        "logDir": logDir,
        "scriptName": scriptName,
        "encoding": encoding,
        "configFile": configFile,
        "baseFile": baseFile,
        "actionDelay": actionDelay,
        "typingDelay": typingDelay,
        "runInterval": runInterval,
        "runTimeout": runTimeout,
        "doubleClickDelay": doubleClickDelay,
        "searchBackoffDuration": searchBackoffDuration,
        "searchWarningThreshold": searchWarningThreshold,
        "searchCutoffCount": searchCutoffCount,
        "searchShowingOnly": searchShowingOnly,
        "defaultDelay": defaultDelay,
        "childrenLimit": childrenLimit,
        "gtk4Offset": gtk4Offset,
        "debugSearching": debugSearching,
        "debugSleep": debugSleep,
        "debugSearchPaths": debugSearchPaths,
        "logDebugToStdOut": logDebugToStdOut,
        "absoluteNodePaths": absoluteNodePaths,
        "ensureSensitivity": ensureSensitivity,
        "debugTranslation": debugTranslation,
        "blinkOnActions": blinkOnActions,
        "fatalErrors": fatalErrors,
        "checkForA11y": checkForA11y,
        "logDebugToFile": logDebugToFile,
    }

    invalid_value = "__INVALID__"

    def __setattr__(self, option_id, value_to_set):
        if option_id not in self.options:
            raise AttributeError(f"Attempt to use invalid option '{option_id}'.")

        if self.options[option_id] != value_to_set:
            self.options[option_id] = value_to_set


    def __getattr__(self, name):
        try:
            self.options[name]
        except KeyError as error:
            raise AttributeError(f"Attempt to use invalid option '{name}'.") from error


if __name__ == "__main__":
    # Call the function to read the configuration file
    config_data = _Config()

    # Print the retrieved values
    for key, value in config_data.items():
        print(f"{key:25}: {value}")
else:
    config = _Config()
