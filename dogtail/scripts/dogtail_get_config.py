#!/usr/bin/env python3
"""
Print default configuration.
"""

from dogtail.config import config

def main():
    # Print the retrieved values

    print("Configuration.")
    for key, value in config.options.items():
        print(f"{key:25}: {value.value} {value.defined_types}")

if __name__ == "__main__":
    main()
