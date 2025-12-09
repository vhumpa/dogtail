#!/usr/bin/env python3
"""
Create configuration in your current directory.
"""

# pylint: disable=invalid-name

import os
import sys
from dogtail.config import CONFIG_SCHEMA as schema

def main():
    directory = os.path.realpath(os.getcwd())

    configuration = ""

    for section in schema.keys():
        configuration += f"[{section}]\n"
        for key, scheme_value in schema[section].items():
            _, raw_value = scheme_value
            configuration += f"{key} = {raw_value}\n"

    try:
        if os.path.isfile("dogtail_config.ini"):
            print("Configuration file already exists.")
            sys.exit(0)

        with open(directory + "/dogtail_config.ini", "w", encoding="utf-8") as _file:
            _file.write(configuration)

        print(" ".join((
            "File was successfully created.",
            os.path.abspath(os.path.join(directory, "dogtail_config.ini")),
        )))

    except IOError as error:
        raise IOError("File creation of 'dogtail_config.ini' failed.") from error

if __name__ == "__main__":
    main()
