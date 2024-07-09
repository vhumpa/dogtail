
#/usr/bin/python3
"""
Experimental dogtail changes for 1.0 release.
"""

# ruff: noqa: E501

import configparser
from configparser import NoSectionError

from dogtail.logging import logging_class
LOGGING = logging_class.logger


class Value:
    """
    Value class to keep value and its types.
    """

    def __init__(self, set_value, defined_types=list):
        self.value = set_value
        self.defined_types = defined_types


class _Config:
    """
    Config class to keep backwards compatibility and to have getters and setters.
    """

    # Create a ConfigParser object.
    cfg = configparser.ConfigParser()

    # Read the configuration file.
    # TODO Figure out where the file will be.
    cfg.read("config.ini")

    NO_VALUES = ["", "n", "no", "f", "false", "False", "0"]

    # Access values from the configuration file.

    # Timing Delay section.
    section = "timing_section"
    _action_delay = float(cfg.get(section, "action_delay", fallback=1.0))
    _typing_delay = float(cfg.get(section, "typing_delay", fallback=0.1))
    _default_delay = float(cfg.get(section, "default_delay", fallback=0.5))
    _double_click_delay = float(cfg.get(section, "double_click_delay", fallback=0.1))
    _search_back_off_delay = float(cfg.get(section, "search_back_off_delay", fallback=0.5))

    # Searching section.
    section = "searching"
    _search_warning_threshold = int(cfg.get(section, "search_warning_threshold", fallback=3))
    _search_cut_off_limit = int(cfg.get(section, "search_cut_off_limit", fallback=20))
    _search_showing_only = cfg.get(section, "search_showing_only", fallback="False") not in NO_VALUES

    # Children Limit section.
    section = "children_limit"
    _children_limit = int(cfg.get(section, "children_limit", fallback=100))

    # Util Scripts section.
    section = "util_scripts"
    _run_interval = float(cfg.get(section, "run_interval", fallback=0.5))
    _run_timeout = int(cfg.get(section, "run_timeout", fallback=30))

    # GTK4Offset section.
    section = "gtk4_offset"
    _offset = list(cfg.get(section, "offset", fallback=(12, 12)))

    # Debug section.
    section = "debug"
    _debug_dogtail = cfg.get(section, "debug_dogtail", fallback="False") not in NO_VALUES
    _debug_searching = cfg.get(section, "debug_searching", fallback="False") not in NO_VALUES
    _debug_sleep = cfg.get(section, "debug_sleep", fallback="False") not in NO_VALUES
    _debug_search_paths = cfg.get(section, "debug_search_paths", fallback="False") not in NO_VALUES

    # Debug section.
    section = "setting"
    _log_debug_to_std_out = cfg.get(section, "log_debug_to_std_out", fallback="True") not in NO_VALUES
    _log_debug_to_file = cfg.get(section, "log_debug_to_file", fallback="False") not in NO_VALUES
    _absolute_node_paths = cfg.get(section, "absolute_node_paths", fallback="False") not in NO_VALUES
    _ensure_sensitivity = cfg.get(section, "ensure_sensitivity", fallback="False") not in NO_VALUES
    _fatal_errors = cfg.get(section, "fatal_errors", fallback="False") not in NO_VALUES
    _check_for_a11y = cfg.get(section, "check_for_a11y", fallback="True") not in NO_VALUES

    # Return a dictionary with the retrieved values
    options = {
        "action_delay": Value(_action_delay, [float, int]),
        "typing_delay": Value(_typing_delay, [float, int]),
        "default_delay": Value(_default_delay, [float, int]),
        "double_click_delay": Value(_double_click_delay, [float, int]),
        "search_back_off_delay": Value(_search_back_off_delay, [float, int]),

        "search_warning_threshold": Value(_search_warning_threshold, [int]),
        "search_cut_off_limit": Value(_search_cut_off_limit, [int]),
        "search_showing_only": Value(_search_showing_only, [bool]),

        "children_limit": Value(_children_limit, [int]),

        "run_interval": Value(_run_interval, [float, int]),
        "run_timeout": Value(_run_timeout, [float, int]),

        "gtk4_offset": Value(_offset, [list]),

        "debug_dogtail": Value(_debug_dogtail, [bool]),
        "debug_searching": Value(_debug_searching, [bool]),
        "debug_sleep": Value(_debug_sleep, [bool]),
        "debug_search_paths": Value(_debug_search_paths, [bool]),

        "log_debug_to_std_out": Value(_log_debug_to_std_out, [bool]),
        "log_debug_to_file": Value(_log_debug_to_file, [bool]),
        "absolute_node_paths": Value(_absolute_node_paths, [bool]),
        "ensure_sensitivity": Value(_ensure_sensitivity, [bool]),
        "fatal_errors": Value(_fatal_errors, [bool]),
        "check_for_a11y": Value(_check_for_a11y, [bool]),
    }

    # Custom user section.
    section = "user_setting"
    try:
        user_setting_dictionary = dict(cfg.items(section))

        # Set all user setup.
        for key, value in user_setting_dictionary.items():
            # Should we force 'custom_' prefix on users?
            # As of now I opted to not do that, users can define any option they want.
            options[key] = Value(value, [type(value)])

    except NoSectionError:
        # Do nothing, no user setting defined, which is ok.
        pass

    except Exception as error:
        raise RuntimeError("Unexpected exception caught.") from error


    def adjust_casing(self, string_to_fix):
        """
        Transforms a string to snake_case.

        :param string_to_fix: String to transform to snake_case
        :type string_to_fix: str

        :return: Transformed string.
        :rtype: str
        """

        string_in_snake_case = ""
        for character in string_to_fix:
            if character.isalpha and character.isupper():
                string_in_snake_case += "_" + character.lower()
            else:
                string_in_snake_case += character

        return string_in_snake_case

    def __setattr__(self, option_id, value_to_set):
        # TODO development only, set to .debug before release.
        LOGGING.info(logging_class.get_func_params_and_values())

        # Set a variable to use for the setter logic.
        set_option_id = option_id

        # Attempt to have some backwards compatibility and support camelCase.
        if any(char.isupper() for char in set_option_id):
            set_option_id = self.adjust_casing(set_option_id)
            LOGGING.info(f"Value was transformed to '{set_option_id}'.")

        # Set custom user value to use in dogtail run.
        # Current logic will fail on any attempt not set in config.ini.
        # Should we allow setting values during a dogtail execution?
        # if "custom_" in set_option_id:
        #     LOGGING.info(f"Setting a custom user value '{set_option_id}'.")
        #     self.options[set_option_id] = value_to_set

        # In other cases check that the value exists.
        if set_option_id not in self.options:
            #LOGGING.info("To define a custom value, use 'custom_' to prefix your value.")
            raise AttributeError(f"Attempt to use invalid option '{set_option_id}'.")

        # Set the value if the value is not already present.
        if self.options[set_option_id].value != value_to_set:
            # Defined types variable.
            _defined_types = self.options[set_option_id].defined_types

            # Type checking.
            if type(value_to_set) not in _defined_types:
                raise ValueError(" ".join((
                    f"Attempt to set value of type '{type(value_to_set)}'",
                    f"to key with accepted types '{_defined_types}'",
                )))

            # Type was checked, keep the defined types.
            self.options[set_option_id] = Value(value_to_set, _defined_types)

    def __getattr__(self, option_id):
        # TODO development only, set to .debug before release.
        LOGGING.info(logging_class.get_func_params_and_values())

        # Set a variable to use for the getter logic.
        get_option_id = option_id

        # Attempt to have some backwards compatibility and support camelCase.
        if any(char.isupper() for char in get_option_id):
            get_option_id = self.adjust_casing(get_option_id)
            LOGGING.info(f"Value was transformed to '{get_option_id}'.")

        try:
            return self.options[get_option_id].value
        except KeyError as error:
            raise AttributeError(f"Attempt to use invalid option '{get_option_id}'.") from error


if __name__ == "__main__":
    # Call the function to read the configuration file
    config_data = _Config()

    # Print the retrieved values
    for key, value in config_data.items():
        print(f"{key:25}: {value}")
else:
    config = _Config()
