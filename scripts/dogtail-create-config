#!/usr/bin/env python3
"""
Create configuration in your current directory.
"""

# pylint: disable=invalid-name

import os
import sys
from dogtail.config import config

def main():
    directory = os.path.realpath(os.getcwd())


    # Print the retrieved values

    configuration = ""
    configuration += "[config]\n"

    for key, value in config.options.items():
        configuration += f"{key} = {value.value}\n"

    configuration += "[user_config]\n"
    configuration += "user_value_x = user_value_x\n"
    configuration += "user_value_y = user_value_y\n"
    configuration += "user_value_z = user_value_z\n"

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
