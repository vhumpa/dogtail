#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=line-too-long
# ruff: noqa: E501

import configparser
from configparser import NoSectionError

import copy

from dogtail.logging import logging_class
LOGGING = logging_class.logger


NO_VALUES = ["", "n", "no", "f", "false", "False", "0"]


class Value:
    """
    Value class to keep value and its types.
    """

    def __init__(self, set_value, defined_types=list):
        self.value = set_value
        self.defined_types = defined_types

    def __str__(self):
        return f"Default Value: '{self.value}'. Defined Types: '{str(self.defined_types)}'"

    def __repr__(self):
        return self.__str__()


class LoadDefaultConfiguration:
    """
    Configuration class for default values.
    """

    def __init__(self, config_parser):
        # Access values from the configuration file.
        self.cfg = config_parser

        # Timing Delay section.
        section = "config"
        self.action_delay = float(self.cfg.get(section, "action_delay", fallback=1))
        self.typing_delay = float(self.cfg.get(section, "typing_delay", fallback=0.1))
        self.default_delay = float(self.cfg.get(section, "default_delay", fallback=0.5))
        self.double_click_delay = float(self.cfg.get(section, "double_click_delay", fallback=0.1))
        self.search_back_off_delay = float(self.cfg.get(section, "search_back_off_delay", fallback=0.5))

        # Searching section.
        self.search_warning_threshold = int(self.cfg.get(section, "search_warning_threshold", fallback=3))
        self.search_cut_off_limit = int(self.cfg.get(section, "search_cut_off_limit", fallback=20))
        self.search_showing_only = self.cfg.get(section, "search_showing_only", fallback="False") not in NO_VALUES

        # Children Limit section.
        self.children_limit = int(self.cfg.get(section, "children_limit", fallback=100))

        # Util Scripts section.
        self.run_interval = float(self.cfg.get(section, "run_interval", fallback=0.5))
        self.run_timeout = int(self.cfg.get(section, "run_timeout", fallback=30))

        # GTK4Offset section.
        self.offset = list(self.cfg.get(section, "offset", fallback=(12, 12)))

        # Debug section.
        self.debug_dogtail = self.cfg.get(section, "debug_dogtail", fallback="False") not in NO_VALUES
        self.debug_file = self.cfg.get(section, "debug_file", fallback="/tmp/dogtail_debug.log")

        # Other debug section.
        self.debug_searching = self.cfg.get(section, "debug_searching", fallback="False") not in NO_VALUES
        self.debug_sleep = self.cfg.get(section, "debug_sleep", fallback="False") not in NO_VALUES
        self.debug_search_paths = self.cfg.get(section, "debug_search_paths", fallback="False") not in NO_VALUES

        # Debug section. ?
        #self.log_debug_to_std_out = self.cfg.get(section, "log_debug_to_std_out", fallback="True") not in NO_VALUES
        self.absolute_node_paths = self.cfg.get(section, "absolute_node_paths", fallback="False") not in NO_VALUES
        self.ensure_sensitivity = self.cfg.get(section, "ensure_sensitivity", fallback="False") not in NO_VALUES
        self.fatal_errors = self.cfg.get(section, "fatal_errors", fallback="False") not in NO_VALUES
        self.check_for_a11y = self.cfg.get(section, "check_for_a11y", fallback="True") not in NO_VALUES

        if self.debug_dogtail:
            LOGGING.info("Debugging dogtail to console.")
            logging_class.debug_to_console()


class _Config:
    """
    Config class to keep backwards compatibility and to have getters and setters.
    """

    # Create a ConfigParser object.
    config_parser = configparser.ConfigParser()

    # Read the configuration file.
    successful_file_parsed = config_parser.read("dogtail_config.ini")
    _default = LoadDefaultConfiguration(config_parser)

    # Return a dictionary with the retrieved values.
    # Define allowed type so that user cannot by mistake set different type than allowed.
    options = {
        "action_delay": Value(_default.action_delay, [float, int]),
        "typing_delay": Value(_default.typing_delay, [float, int]),
        "default_delay": Value(_default.default_delay, [float, int]),
        "double_click_delay": Value(_default.double_click_delay, [float, int]),
        "search_back_off_delay": Value(_default.search_back_off_delay, [float, int]),

        "search_warning_threshold": Value(_default.search_warning_threshold, [int]),
        "search_cut_off_limit": Value(_default.search_cut_off_limit, [int]),
        "search_showing_only": Value(_default.search_showing_only, [bool]),

        "children_limit": Value(_default.children_limit, [int]),

        "run_interval": Value(_default.run_interval, [float, int]),
        "run_timeout": Value(_default.run_timeout, [float, int]),

        "gtk4_offset": Value(_default.offset, [list, tuple]),

        "debug_dogtail": Value(_default.debug_dogtail, [bool]),
        "debug_file": Value(_default.debug_file, [str]),

        "debug_searching": Value(_default.debug_searching, [bool]),
        "debug_sleep": Value(_default.debug_sleep, [bool]),
        "debug_search_paths": Value(_default.debug_search_paths, [bool]),

        #"log_debug_to_std_out": Value(_default.log_debug_to_std_out, [bool]),
        "absolute_node_paths": Value(_default.absolute_node_paths, [bool]),
        "ensure_sensitivity": Value(_default.ensure_sensitivity, [bool]),
        "fatal_errors": Value(_default.fatal_errors, [bool]),
        "check_for_a11y": Value(_default.check_for_a11y, [bool]),
    }

    # Create a deep copy instead of shallow copy to keep values for reset method.
    _default_values_storage = copy.deepcopy(options)

    # User configuration.
    section = "user_config"
    try:
        user_setting_dictionary = dict(_default.cfg.items(section))

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


    def reset_configuration(self):
        """
        Reset configuration to default values.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        self.options.update(self._default_values_storage)


    def adjust_casing(self, string_to_fix):
        """
        Transforms a string to snake_case.

        :param string_to_fix: String to transform to snake_case
        :type string_to_fix: str

        :return: Transformed string.
        :rtype: str
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        string_in_snake_case = ""
        for character in string_to_fix:
            if character.isalpha and character.isupper():
                string_in_snake_case += "_" + character.lower()
            else:
                string_in_snake_case += character

        return string_in_snake_case


    def __setattr__(self, option_id, value_to_set):
        LOGGING.debug(logging_class.get_func_params_and_values())

        # Set a variable to use for the setter logic.
        set_option_id = option_id

        # Attempt to have some backwards compatibility and support camelCase.
        if any(char.isupper() for char in set_option_id):
            set_option_id = self.adjust_casing(set_option_id)
            LOGGING.debug(f"Value was transformed to '{set_option_id}'.")

        # Set custom user value to use in dogtail run.
        # Current logic will fail on any attempt not set in config.ini.
        # Should we allow setting values during a dogtail execution?
        # if "custom_" in set_option_id:
        #     LOGGING.info(f"Setting a custom user value '{set_option_id}'.")
        #     self.options[set_option_id] = value_to_set

        # In other cases check that the value exists.
        if set_option_id not in self.options:
            raise AttributeError(f"Attempt to use invalid option '{set_option_id}'.")
            # LOGGING.info(f"Attempt to use invalid option '{set_option_id}'.")
            # return

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

            if set_option_id == "debug_dogtail" and self.options[set_option_id].value:
                LOGGING.info("Debugging dogtail to console.")
                logging_class.debug_to_console()

            if set_option_id == "debug_dogtail" and not self.options[set_option_id].value:
                LOGGING.info("Disabling debugging dogtail to console.")
                logging_class.disable_debug_to_console()


    def __getattr__(self, option_id):
        # Set a variable to use for the getter logic.
        get_option_id = option_id

        # Attempt to have some backwards compatibility and support camelCase.
        if any(char.isupper() for char in get_option_id):
            get_option_id = self.adjust_casing(get_option_id)
            LOGGING.debug(f"Value was transformed to '{get_option_id}'.")

        try:
            return self.options[get_option_id].value
        except KeyError as error:
            raise AttributeError(f"Attempt to use invalid option '{get_option_id}'.") from error
            # LOGGING.info(f"Attempt to use invalid option '{get_option_id}'.")


config = _Config()
