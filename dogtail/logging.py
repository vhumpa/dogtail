#!/usr/bin/python3
"""
This file provides loggers.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel


import os
import sys
import logging

# Singleton solution provided by https://stackoverflow.com/a/54209647

class Singleton(type):
    """
    Singleton class used as metaclass by :py:class:`logger.Logging`.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logging(metaclass=Singleton):
    """
    Logging class.
    """

    logger = None
    default_log_file = "/tmp/dogtail_debug.log"

    def __init__(self) -> None:
        """
        Initiating logger class with some basic logging setup.
        """

        # Preventing circular import, we only need one value for logging.
        import configparser
        config_parser = configparser.ConfigParser()
        config_parser.read("dogtail_config.ini")
        self.debug_file = config_parser.get(
            "config",
            "debug_file",
            fallback=self.default_log_file
        )
        # Validate the debug file value.
        self.debug_file = None if self.debug_file == "None" else self.debug_file

        self.debug_file_persistence = config_parser.get(
            "config",
            "debug_file_persistence",
            fallback=False
        )
        # Validate the debug file persistence value.
        self.debug_file_persistence = True if self.debug_file_persistence == "True" else False

        # Nulling the file based persistence config value.
        if not self.debug_file_persistence:
            self.dogtail_truncate_the_logger_file()

        self.logger = logging.getLogger("__dogtail_logger__")
        self.logger.setLevel(logging.DEBUG)

        # Disable default handler.
        self.logger.propagate = False

        formatter = logging.Formatter(
            "".join((
                "[%(levelname)s] %(asctime)s: ",
                "[%(filename)s:%(lineno)d] ",
                "%(func_name)s: %(message)s"
            ))
        )

        # Default umask is 0o022 which turns off permissions for groups and others.
        # We need the logger file to be readable and modifiable by anyone.
        os.umask(0)

        # Setup of file handler.
        # All DEBUG and higher level logs will be going to the file.
        if self.debug_file:
            file_handler = logging.FileHandler(self.debug_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            file_handler.set_name("file_handler")

            # Add file handler only if file is defined.
            self.logger.addHandler(file_handler)

        # Setup of console handler.
        # All INFO and higher level logs will be going to the console.
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        console_handler.set_name("console_handler")

        # Add console handler.
        self.logger.addHandler(console_handler)

        self.logger.addFilter(FuncFilter())

    def debug_to_console(self) -> None:
        """
        Set file handler level to DEBUG to get the output to console.
        """

        for handler in self.logger.handlers:
            if handler.get_name() == "console_handler":
                handler.setLevel(logging.DEBUG)
                break

    def disable_debug_to_console(self) -> None:
        """
        Set file handler level to INFO to get the output to console.
        """

        for handler in self.logger.handlers:
            if handler.get_name() == "console_handler":
                handler.setLevel(logging.INFO)
                break

    def get_func_params_and_values(self):
        """
        Simple way to have logging data from the place it was called in.
        """

        try:
            frame = sys._getframe().f_back
            _local_func_parameters = frame.f_locals.keys()
            _local_func_parameters_value = frame.f_locals.values()

            # ATTENTION: Never change this from repr() to str().
            # In case of .name .role_name and .description when log is called it goes
            # to the Node's __str__ which will want to represent the node with
            # name role_name and description causing it to get logged again and again
            # wanting to go the __str__ representation.
            # Causing infinite recursion.
            # The need to do it this way is for backwards compatibility.
            # Logging is new so we have to work around it.
            map_of_keys_and_values = [
                x if "self" == x else x if "context" == x else repr(x) + "=" + repr(y)
                for x, y in zip(_local_func_parameters, _local_func_parameters_value)
            ]
            return f"({', '.join(map_of_keys_and_values)})"
        except Exception as error:
            self.logger.error("Error in get_func_params_and_values: %s", error)
            return ""

    def dogtail_truncate_the_logger_file(self) -> None:
        """
        If the Logging class is used from multiple files or scripts especially when
        running one script from another, the logger would not be found and file is
        deleted, making previous logs disappear.

        Lets just null the file only on request.
        """

        # Null the file only if it exists.
        # If it does not, no problem, do nothing.
        if os.path.isfile(self.debug_file):
            # Default umask is 0o022 which turns off permissions for groups and others.
            os.umask(0)

            # Create a specific file descriptor for our needs with proper permissions.
            descriptor = os.open(
                path=self.debug_file,
                flags=(os.O_CREAT | os.O_TRUNC),  # Create if not existing, truncate.
                mode=0o666,
            )
            # Close the file descriptor.
            os.close(descriptor)

class FuncFilter(logging.Filter):
    """
    Filter Class to get exact wanted frame.
    """

    def filter(self, record):
        # Have to walk the frame a bit back.
        # 1. filter, 2. handle, 3. _log, 4. debug, 5. Original calling function.
        record.func_name = str(
            sys._getframe().f_back.f_back.f_back.f_back.f_back.f_code.co_name
        )
        return True

logging_class = Logging()
