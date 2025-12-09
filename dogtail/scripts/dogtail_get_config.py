#!/usr/bin/env python3
"""
Print default configuration.
"""

from dogtail.config import config, CONFIG_SCHEMA

def main():
    # Print the retrieved values

    print("Configuration.")

    expected_types = {}
    header_options = "Config Options"
    header_value = "Value"
    header_type = "Acceptable Types"

    max_string_options_length = len(header_options)
    max_string_value_length = len(header_value)

    for section, fields in CONFIG_SCHEMA.items():
        for key, (expected_type, default_value) in fields.items():
            expected_types[key] = (expected_type, default_value)

    for key, value in config.validated_config.items():
        max_string_options_length = max(max_string_options_length, len(key))
        max_string_value_length = max(max_string_value_length, len(str(value)))

    print(f"{header_options:<{max_string_options_length+2}} {header_value:<{max_string_value_length+1}} {header_type}")

    for key, value in config.validated_config.items():
        expected_type = "object"
        if key in expected_types.keys():
            expected_type = str(expected_types[key][0])
        print(f"{key:<{max_string_options_length + 1}}: {str(value):<{max_string_value_length + 1}} '{expected_type}'")

if __name__ == "__main__":
    main()
