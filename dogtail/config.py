#!/usr/bin/python3
"""
Experimental dogtail changes for 2.0 release.
"""

# pylint: disable=line-too-long
# ruff: noqa: E501

import configparser

from typing import get_origin, get_args

import copy

from dogtail.logging import logging_class
LOGGING = logging_class.logger


YES_VALUES = ["y", "yes", "t", "true", "True", "1"]
NO_VALUES = ["", "n", "no", "f", "false", "False", "0"]


CONFIG_SCHEMA = {
    "config": {
        "action_delay": ([float, int], 1),
        "typing_delay": ([float, int], 0.1),
        "default_delay":([float, int], 0.5),
        "double_click_delay": ([float, int], 0.1),
        "search_back_off_delay": ([float, int], 0.5),
        "search_warning_threshold": (int, 3),
        "search_cut_off_limit": (int, 20),
        "search_showing_only": (bool, False),
        "children_limit": (int, 100),
        "run_interval": ([float, int], 0.5),
        "run_timeout": ([float, int], 30),
        "gtk4_offset": ([list[int], tuple[int]], [12, 12]),
        "debug_dogtail": (bool, False),
        "debug_file": (str, "/tmp/dogtail_debug.log"),
        "debug_searching": (bool, False),
        "debug_sleep": (bool, False),
        "debug_search_paths": (bool, False),
        "absolute_node_paths": (bool, False),
        "ensure_sensitivity": (bool, False),
        "fatal_errors": (bool, False),
        "check_for_a11y": (bool, True),
    },
    "user_config": {
        "user_value_x": (object, "user_value_x"),
    },
}


class ConfigValidationError(Exception):
    pass


def cast_basic(value: str, expected_type):
    """
    Casts primitive types.
    """

    if isinstance(value, str) and expected_type is bool:
        lower = value.lower()

        if lower in YES_VALUES:
            return True

        if lower in NO_VALUES:
            return False

        raise ValueError(f"Invalid boolean: {value}")

    return expected_type(value)


def cast_sequence(value: str, expected_container):
    """
    Casts comma-separated values into list[...] or tuple[...].
    """

    origin = get_origin(expected_container)
    (item_type,) = get_args(expected_container)

    # Strip optional list/tuple brackets like [1,2,3] or (1,2,3).
    cleaned = value.strip()
    if (cleaned.startswith("[") and cleaned.endswith("]")) or \
       (cleaned.startswith("(") and cleaned.endswith(")")):
        cleaned = cleaned[1:-1].strip()

    # Split by comma.
    items = [x.strip() for x in cleaned.split(",") if x.strip()]

    casted = [cast_value(x, item_type) for x in items]

    if origin is list:
        return casted

    if origin is tuple:
        return tuple(casted)

    raise ValueError(f"Unsupported sequence type: {origin}")


def cast_value(value, expected_type):
    # --- Union-of-types support ---
    if isinstance(expected_type, list):
        errors = []
        for t in expected_type:
            try:
                return cast_value(value, t)
            except Exception as e:
                errors.append(str(e))
        raise ValueError(" | ".join(errors))

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # --- Handle sequences ---
    if origin in (list, tuple):
        # If value is already the correct container type, just validate inner types
        if isinstance(value, origin):
            if args:
                item_type = args[0]
                for i, item in enumerate(value):
                    if not isinstance(item, item_type):
                        raise ValueError(f"Element '{i}' in '{value}' is not of type '{item_type}'.")
            return value
        # Otherwise parse string into sequence
        return cast_sequence(value, expected_type)

    # --- Handle simple types ---
    # If value is already of correct type, return.
    if isinstance(value, expected_type):
        return value

    # If the value is object.
    if expected_type is object:
        return value

    # Otherwise, cast string to type
    return cast_basic(value, expected_type)


def load_and_validate_config(path: str, schema: dict):
    config = configparser.ConfigParser()
    config.read(path)

    validated = {}

    # We do not care about config sections in dogtail, just set the variables to a dict.

    # Step 1: Process all sections found in the file, even if not in schema.
    LOGGING.debug("Process all variables.")
    for section in config.sections():

        for key, raw_value in config[section].items():
            # If schema defines type → validate
            if section in schema and key in schema[section]:
                expected_type, default_value = schema[section][key]

                try:
                    value = cast_value(raw_value, expected_type)
                except Exception as e:
                    raise ConfigValidationError(
                        f"Type error in [{section}].{key}: {e}"
                    )

                validated[key] = value
                LOGGING.debug(f"Set Validated key '{key}' to value '{value}'")

            else:
                # Unknown key → keep raw value as string
                validated[key] = raw_value
                LOGGING.debug(f"Set Validated key '{key}' to raw value '{raw_value}'")

    LOGGING.debug("Process default variables.")
    # Step 2: Ensure missing schema sections & keys get default values.
    for section, fields in schema.items():
        for key, (expected_type, default_value) in fields.items():
            if key not in validated:
                validated[key] = default_value
                LOGGING.debug(f"Set Default key '{key}' to value '{default_value}'")

    return validated


class _Config:
    """
    Config class to keep backwards compatibility and to have getters and setters.
    """

    validated_config = load_and_validate_config("dogtail_config.ini", CONFIG_SCHEMA)
    LOGGING.debug(f"Validated config: '{validated_config}'")

    # Create a deep copy instead of shallow copy to keep values for reset method.
    _default_values_storage = copy.deepcopy(validated_config)

    # Handle dogtail debug logging.
    if validated_config["debug_dogtail"]:
        LOGGING.info("Debugging dogtail to console.")
        logging_class.debug_to_console()


    def reset_configuration(self):
        """
        Reset configuration to default values.
        """

        LOGGING.debug(logging_class.get_func_params_and_values())

        self.validated_config.update(self._default_values_storage)


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
            LOGGING.debug(f"Config variable was transformed to '{set_option_id}'.")

        # Set custom user value to use in dogtail run.
        # Current logic will fail on any attempt not set in config.ini.
        # Should we allow setting values during a dogtail execution?
        # if "custom_" in set_option_id:
        #     LOGGING.info(f"Setting a custom user value '{set_option_id}'.")
        #     self.options[set_option_id] = value_to_set

        # In other cases check that the value exists.
        if set_option_id not in self.validated_config:
            raise AttributeError(f"Attempt to use invalid option '{set_option_id}'.")
            # LOGGING.info(f"Attempt to use invalid option '{set_option_id}'.")
            # return

        # Set the value if the value is not already present.
        if self.validated_config[set_option_id] != value_to_set:

            validated_expected_type = None

            # First attempt to get defaults from the schema.
            for section in CONFIG_SCHEMA.keys():
                if set_option_id in CONFIG_SCHEMA[section]:
                    validated_expected_type, default_value = CONFIG_SCHEMA[section][set_option_id]

            # If unsuccessful mark the expected type as anything.
            if not validated_expected_type:
                LOGGING.debug("Setting expected type to object.")
                validated_expected_type = object

            try:
                # Set the value.
                self.validated_config[set_option_id] = cast_value(value_to_set, validated_expected_type)
            except Exception:
                # Log the message but do not end, use the default.
                LOGGING.info(" ".join((
                    f"Attempt to set value of type '{type(value_to_set)}'",
                    f"to key with accepted types '{validated_expected_type}'",
                )))
                # Setting the value.
                LOGGING.info(f"Fallback of config option '{set_option_id}' to '{default_value}'.")
                self.validated_config[set_option_id] = default_value

            if set_option_id == "debug_dogtail" and self.validated_config[set_option_id]:
                LOGGING.info("Debugging dogtail to console.")
                logging_class.debug_to_console()

            if set_option_id == "debug_dogtail" and not self.validated_config[set_option_id]:
                LOGGING.info("Disabling debugging dogtail to console.")
                logging_class.disable_debug_to_console()


    def __getattr__(self, option_id):
        # Set a variable to use for the getter logic.
        get_option_id = option_id

        # Attempt to have some backwards compatibility and support camelCase.
        if any(char.isupper() for char in get_option_id):
            get_option_id = self.adjust_casing(get_option_id)
            LOGGING.debug(f"Config variable was transformed to '{get_option_id}'.")
            LOGGING.debug(f"Its value is '{self.validated_config[get_option_id]}'.")

        try:
            return self.validated_config[get_option_id]
        except KeyError as error:
            raise AttributeError(f"Attempt to use invalid option '{get_option_id}'.") from error
            # LOGGING.info(f"Attempt to use invalid option '{get_option_id}'.")


config = _Config()
