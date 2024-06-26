
#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

import configparser

# TODO might be worth keeping getters and setters to the dictionary.
def read_config():
    """
    Read config values from config.ini file and return them as dictionary.

    :return: Dictionary of configuration values.
    :rtype: dict
    """
    # Create a ConfigParser object.
    config = configparser.ConfigParser()

    # Read the configuration file.
    config.read("config.ini")

    NO_VALUES = ["", "n", "no", "f", "false", "False", "0"]

    # Access values from the configuration file.
    # Timing Delay section.
    section = "TimingDelay"
    action_delay = config.get(section, "action_delay", fallback="VALUE TO SET IF INI NOT FOUND")
    typing_delay = config.get(section, "typing_delay")
    default_delay = config.get(section, "default_delay")
    double_click_delay = config.get(section, "double_click_delay")
    search_back_off_delay = config.get(section, "search_back_off_delay")

    # Searching section.
    section = "Searching"
    search_warning_threshold = config.get(section, "search_warning_threshold")
    search_cut_off_limit = config.get(section, "search_cut_off_limit")
    search_showing_only = config.get(section, "search_showing_only") not in NO_VALUES

    # Children Limit section.
    section = "ChildrenLimit"
    children_limit = config.get(section, "children_limit")

    # Util Scripts section.
    section = "UtilScripts"
    run_interval = config.get(section, "run_interval")
    run_timeout = config.get(section, "run_timeout")

    # GTK4Offset section.
    section = "GTK4Offset"
    offset = config.get(section, "offset")

    # Debug section.
    section = "Debug"
    debug_dogtail = config.get(section, "debug_dogtail") not in NO_VALUES
    debug_searching = config.get(section, "debug_searching") not in NO_VALUES
    debug_sleep = config.get(section, "debug_sleep") not in NO_VALUES
    debug_search_paths = config.get(section, "debug_search_paths") not in NO_VALUES

    # Debug section.
    section = "Setting"
    log_to_std_out = config.get(section, "log_to_std_out") not in NO_VALUES
    absolute_node_paths = config.get(section, "absolute_node_paths") not in NO_VALUES
    ensure_sensitivity = config.get(section, "ensure_sensitivity") not in NO_VALUES
    fatal_errors = config.get(section, "fatal_errors") not in NO_VALUES
    check_for_a11y = config.get(section, "check_for_a11y") not in NO_VALUES

###

    # Return a dictionary with the retrieved values
    config_values = {
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
    }

    return config_values


if __name__ == "__main__":
    # Call the function to read the configuration file
    config_data = read_config()

    # Print the retrieved values
    for key, value in config_data.items():
        print(f"{key:25}: {value}")
