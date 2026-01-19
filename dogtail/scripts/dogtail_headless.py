#!/usr/bin/env python3
"""
A dogtail "headless" script that takes care of starting the session in wanted configuration.
"""

# ruff: noqa: E501

# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
# pylint: disable=line-too-long


import os
import errno
import signal
import subprocess
import traceback
from subprocess import check_output, STDOUT, CalledProcessError
import time
import argparse
import configparser
import shutil
import sys
import re


ENVIRONMENT_VARIABLES_TO_PRESERVE = [
    "PYTHONPATH",
    "TEST",
    "TERM",
]


def print_info(string_to_print) -> None:
    """
    Print string.

    :param string_to_print: String to print coloured based on setup.
    :type string_to_print: str
    """

    print("headless: " + str(string_to_print))


def run(command) -> str:
    """
    Utility function to execute given command and return its output.
    """

    try:
        output = check_output(command, shell=True, env=os.environ, stderr=STDOUT, encoding="utf-8")
        return output.strip("\n")
    except CalledProcessError as error:
        return error.output


def run_verbose(command) -> tuple:
    """
    Utility function to execute given command and return its output.
    """

    try:
        output = check_output(command, shell=True, env=os.environ, stderr=STDOUT, encoding="utf-8")
        return (output.strip("\n"), 0, None)
    except CalledProcessError as error:
        return (error.output, error.returncode, error)


def get_initial_environment_dictionary(binary="gnome-session-binary", term=None) -> dict:
    """
    Lets assume initial state of the machine is with already running display manager.
    We need to get environment variables from the session to check correct configuration.
    Print no errors since this will fail when session is not running.
    Returns environment as dictionary.
    """

    return get_environment_dictionary(binary=binary, verbose=False, term=term)


def get_environment_dictionary(binary="gnome-session-binary", verbose=True, term=None) -> dict:
    """
    Targeting the gnome-session-binary process to get all environment variables.
    Returns environment as dictionary.
    """

    environment_dictionary = {}

    user_id = str(os.geteuid())
    gnome_session_binary_pid = None

    try:
        gnome_session_binary_pid = run(f"pgrep -fAu {user_id} {binary}").split("\n")[0]
    except CalledProcessError:
        if verbose:
            print_info(f"Failed to retrieve {binary} pid from pgrep:")
            print_info(f"\n{traceback.format_exc()}")

    # Use a given binary pid to get its environment variables.
    if gnome_session_binary_pid:
        environment_process_path = f"/proc/{gnome_session_binary_pid}/environ"

        # Verify that the environ file can be opened and load environment variables to dictionary.
        try:
            with open(environment_process_path, "r", encoding="utf-8") as environ_file:
                for item in environ_file.read().split("\x00"):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        environment_dictionary[key] = value
        except IOError as error:
            if verbose:
                print_info(f"Environment file manipulation failed on: '{error}'")

        # Preserving wanted environment variables.
        for environment_variable in ENVIRONMENT_VARIABLES_TO_PRESERVE:
            if environment_variable in os.environ:
                environment_dictionary[environment_variable] = os.environ[environment_variable]

        # Check if the TERM variable is set.
        try:
            current_term_variable = os.environ["TERM"]
        except KeyError:
            current_term_variable = None

        # If the user sets the TERM variable, overwrite it, no matter what was there.
        if term is not None:
            environment_dictionary["TERM"] = term
            print_info(f"Setting environment variable TERM as '{term}'")

        # If the variable is not set (should not happen, legacy issue for us) set it.
        elif not current_term_variable:
            environment_dictionary["TERM"] = "xterm-256color"
            print_info("Setting environment variable TERM as 'xterm-256color'")

        # Keep current variable in all other cases.
        else:
            environment_dictionary["TERM"] = current_term_variable

        if "XAUTHORITY" not in environment_dictionary:
            xwaylandauth = ""
            run_user_dir = os.path.abspath(f"/run/user/{user_id}/")

            # Attempt to prevent race conditions, give it at most 5 seconds to appear.
            for _ in range(5):
                # Iterate over the files.
                for _file in os.scandir(run_user_dir):
                    # Check for the file we need.
                    if _file.is_file() and "Xwaylandauth" in _file.path or "xauth" in _file.path:
                        # Set the file to the variable.
                        xwaylandauth = _file.path
                        break

                # We only care about xauthority variable in non-initial call.
                if xwaylandauth == "" and verbose:
                    print_info("Environment variable XAUTHORITY is unavailable, retrying.")
                    time.sleep(1)

            if verbose:
                print_info(f"Setting environment variable XAUTHORITY as '{xwaylandauth}'")

            environment_dictionary["XAUTHORITY"] = xwaylandauth

        return environment_dictionary

    if verbose:
        print_info("Environment file not found, most likely caused by display manager not running.")

    return environment_dictionary


def is_binary_existing_and_executable(path) -> bool:
    """
    Test if given binary file exists.
    """

    if (
        path.startswith(os.path.sep)
        or path.startswith(os.path.join(".", ""))
        or path.startswith(os.path.join("..", ""))
    ):
        if not os.path.exists(path):
            raise IOError(errno.ENOENT, "No such file", path)

        if not os.access(path, os.X_OK):
            raise IOError(errno.ENOEXEC, "Permission denied", path)

    return True


def verify_file_ownership() -> None:
    """
    Verify ownership of the dconf file.
    """

    user_id = os.geteuid()
    file_owner_command = f"sudo stat -c '%U %G' /run/user/{user_id}/dconf/user"

    if not os.path.isfile(f"/run/user/{user_id}/dconf/user"):
        return

    file_owner_command_result = run_verbose(file_owner_command)

    if file_owner_command_result[1] == 0 and "root" in file_owner_command_result[0]:
        print_info("Attempting to restore dconf file ownership.")
        run(f"sudo rm -rf /run/user/{user_id}/dconf/user")
    elif file_owner_command_result[1] != 0:
        print_info("Issue was detected and might need attention")
        print_info(f"\n{file_owner_command_result}")

###
def parse():
    """
    Parser for arguments given to the script.

    :return: Namespace object with attributes parsed out of the command line.
    :rtype: Namespace
    """

    parser = argparse.ArgumentParser(
        prog="$ dogtail-headless",
        description="Adjusted headless script.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "script",
        nargs="?",
        default="bash",
        help="Script to be executed, if not provided 'bash' will be used.",
    )
    parser.add_argument(
        "--session",
        required=False,
        help="\n".join((
            "What session to use (e.g. 'gnome', 'kde-plasma', 'mate').",
            "Comes from /usr/share/xsessions/ or /usr/share/wayland-sessions/."
        ))
    )
    parser.add_argument("--session-binary",
                        required=False,
                        help="Full path to an in-session binary (e.g. '/usr/bin/gnome-shell')."
    )
    parser.add_argument("--dm",
                        required=False,
                        help="\n".join((
                            "What display manager to use for spawning session.",
                            "Supported: 'gdm' (default), 'sddm', or 'lightdm'."
                        ))
    )
    parser.add_argument(
        "--session-type",
        required=False,
        choices=("xorg", "wayland"),
        help="Choose which session type will be used.",
    )
    parser.add_argument(
        "--session-desktop",
        required=False,
        help="Choose which session desktop will be used.",
    )
    parser.add_argument(
        "--display",
        required=False,
        help="Number of the DISPLAY to connect to - default value is ':0'",
    )
    parser.add_argument(
        "--dont-start",
        required=False,
        action="store_true",
        help="Use the system as is. Does not have to be under display manager",
    )
    parser.add_argument(
        "--dont-kill",
        required=False,
        action="store_true",
        help="Do not kill the session when script exits.",
    )
    parser.add_argument(
        "--restart",
        required=False,
        action="store_true",
        help="Restart previously running display manager session before script execution.",
    )
    parser.add_argument(
        "--keep", required=False, help="Number of tests to keep display manager running."
    )
    parser.add_argument(
        "--keep-max",
        required=False,
        action="store_true",
        help="Keep display manager running 'maximum number of tests' times. This equals --dont-kill parameter.",
    )
    parser.add_argument(
        "--disable-a11y",
        required=False,
        action="store_true",
        help="Disable accessibility technologies on script (not session) exit.",
    )
    parser.add_argument(
        "--force",
        required=False,
        action="store_true",
        help="Will check if the configuration was setup correctly. Exit upon fail.",
    )
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        help="Will enable debugging of dogtail.",
    )
    parser.add_argument(
        "--no-color",
        required=False,
        action="store_true",
        help="Do not use colors.",
    )
    parser.add_argument(
        "--allow-duplication",
        required=False,
        action="store_true",
        help="Allow nested/duplicated headless script.",
    )

    parser.add_argument(
        "--no-autologin",
        required=False,
        action="store_true",
        help=argparse.SUPPRESS,
    )

    parser.add_argument(
        "--virtual-monitors",
        choices=("1", "2"),
        required=False,
        help="EXPERIMENTAL: Choose how many virtual monitors to use.",
    )

    parser.add_argument(
        "--term",
        required=False,
        help="Set TERM variable.",
   )

    return parser.parse_args()


class DisplayManager:
    """
    Display Manager class.
    """

    # Display manager presets.

    gdm_options = {
        "config": "/etc/gdm/custom.conf",
        "section": "daemon",
        "enable": "AutomaticLoginEnable",
        "user": "AutomaticLogin"
    }

    sddm_options = {
        "config": "/etc/sddm.conf",
        "section": "Autologin",
        "relogin": "Relogin",
        "session": "Session",
        "user": "User"
    }

    lightdm_options = {
        "config": "/etc/lightdm/lightdm.conf",
        "section": "Seat:*",
        "user": "autologin-user",
        "timeout": "autologin-user-timeout",
        "session": "autologin-session"
    }

    def __init__(
        self,
        session="gnome",
        session_binary="/usr/bin/gnome-shell",
        display_manager="gdm",
        session_type=None,
        session_desktop=None,
        enable_start=True,
        enable_stop=True,
        display_manager_restart=False,
        no_automatic_login=False,
        virtual_monitors=0,
    ) -> None:
        self.enable_start = enable_start
        self.enable_stop = enable_stop
        self.display_manager_restart = display_manager_restart
        self.no_automatic_login = no_automatic_login
        self.virtual_monitors=virtual_monitors

        self.session = session
        self.session_binary = session_binary
        self.display_manager = display_manager

        # Session type is xorg, wayland, None -> respect setting of the system.
        self.session_type = session_type

        # Session desktop is gnome gnome-classic, None -> respect setting of the system.
        self.session_desktop = session_desktop


        if self.display_manager == "gdm":
            self.options = self.gdm_options

        elif self.display_manager == "sddm":
            self.options = self.sddm_options

        elif self.display_manager == "lightdm":
            self.options = self.lightdm_options

        else:
            raise ValueError(f"Unsupported display manager: {self.display_manager}")

        self.session_started_indicator = self.session_binary

        self.user = run("whoami")
        self.user_id = run(f"id -u {self.user}")

        self.config_file = self.options["config"] # e.g. /etc/gdm/custom.conf
        self.temporary_config_file = f"/tmp/{os.path.basename(self.config_file)}"

        # Debugging a11y randomly turning off.
        self.debug_a11y_file = "/usr/lib/systemd/user/org.gnome.SettingsDaemon.A11ySettings.service"
        self.temporary_debug_a11y_file = f"/tmp/{os.path.basename(self.debug_a11y_file)}"

        # GNOME Shell unsafe mode.
        self.unsafe_mode_config_file_shell = "/usr/lib/systemd/user/org.gnome.Shell@wayland.service"
        self.unsafe_mode_config_file_shell_etc = "/etc/systemd/user/org.gnome.Shell@wayland.service"
        self.temporary_unsafe_mode_config_file_shell = f"/tmp/{os.path.basename(self.unsafe_mode_config_file_shell)}"

        # GNOME Kiosk unsafe mode.
        self.unsafe_mode_config_file_kiosk = "/usr/lib/systemd/user/org.gnome.Kiosk@wayland.service"
        self.unsafe_mode_config_file_kiosk_etc = "/etc/systemd/user/org.gnome.Kiosk@wayland.service"

        self.temporary_unsafe_mode_config_file_kiosk = f"/tmp/{os.path.basename(self.unsafe_mode_config_file_kiosk)}"

        self.virtual_monitor_config_file = self.unsafe_mode_config_file_shell
        self.temporary_virtual_monitor_config_file = f"/tmp/{os.path.basename(self.virtual_monitor_config_file)}"

        self.session_restart_required = False

    def restore_config(self) -> None:
        """
        Restore configuration file.
        Not used, but implemented if needed.
        """

        shutil.copy(self.config_file, self.temporary_config_file)

        config_parser = configparser.ConfigParser()
        config_parser.optionxform = str
        config_parser.read(self.temporary_config_file)

        config_parser.remove_option(self.options["section"], self.options["enable"])
        config_parser.remove_option(self.options["section"], self.options["user"])
        config_parser.remove_option(self.options["section"], self.options["timeout"])
        config_parser.remove_option(self.options["section"], self.options["session"])
        config_parser.remove_option(self.options["section"], self.options["relogin"])

        config_parser.remove_option(self.options["section"], "WaylandEnable")

        with open(self.temporary_config_file, "w", encoding="utf-8") as _file:
            config_parser.write(_file)

    def handling_config_setup(self) -> None:
        """
        Handling config setup
        """

        run(f"cp -f {self.config_file} {self.temporary_config_file}")

        config_parser = configparser.ConfigParser()
        # Default option returns lower-case, setting this will make it case sensitive.
        config_parser.optionxform = str
        try:
            config_parser.read(self.temporary_config_file)
        except configparser.Error:
            print_info(f"Unable to parse '{self.options["config"]}'.")
            print(str(traceback.format_exc()))

            print_info(f"Content of '{self.options["config"]}' file:")
            print(run(f"cat {self.temporary_config_file}") + "\n")

            print_info("Exiting headless.")
            sys.exit(1)

        # Section does not exist.
        if not config_parser.has_section(self.options["section"]):
            config_parser.add_section(self.options["section"])

        if self.no_automatic_login:
            print_info("AutomaticLogin and AutomaticLoginEnable disabled.")
            print_info("This is for gnome-initial-setup automation only.")
            print_info("Not setting this in any other case will cause issues.")

            config_parser.remove_option(self.options["section"], self.options["enable"])
            config_parser.remove_option(self.options["section"], self.options["user"])

            time.sleep(1)

        else:
            if self.display_manager == "gdm":
                config_parser.set(self.options["section"], self.options["enable"], "true")
                config_parser.set(self.options["section"], self.options["user"], self.user)

            elif self.display_manager == "sddm":
                config_parser.set(self.options["section"], self.options["relogin"], "false")
                config_parser.set(self.options["section"], self.options["session"], "plasma")
                config_parser.set(self.options["section"], self.options["user"], self.user)

            else: # lightdm
                config_parser.set(self.options["section"], self.options["user"], self.user)
                config_parser.set(self.options["section"], self.options["timeout"], "0")

                if self.session:
                    config_parser.set(self.options["section"], self.options["session"], self.session)

        if self.session_type == "xorg":
            config_parser.set(self.options["section"], "WaylandEnable", "false")

        elif self.session_type == "wayland":
            config_parser.set(self.options["section"], "WaylandEnable", "true")

        # Respecting system setting, get the session that is to be started.
        elif self.session_type is None:
            if "WaylandEnable" in config_parser.options(self.options["section"]):
                # Set xorg only if there is WaylandEnable=false.
                # Wayland should be default everywhere.
                if config_parser.get(self.options["section"], "WaylandEnable") == "false":
                    self.session_type = "xorg"
                else:
                    self.session_type = "wayland"

            # "WaylandEnable" not in config_parser.options("daemon").
            else:
                self.session_type = "wayland"
                config_parser.set(self.options["section"], "WaylandEnable", "true")

        else:
            print_info("This is not acceptable session type. Fallback to the 'xorg' session type")
            print_info("Acceptable names for --session-type: ['xorg', 'wayland']")
            self.session_type = "xorg"
            config_parser.set(self.options["section"], "WaylandEnable", "false")

        with open(self.temporary_config_file, "w", encoding="utf-8") as _file:
            config_parser.write(_file)

        if not os.path.isfile(self.temporary_config_file):
            print_info("Temporary config file was not found, waiting a bit...")
            time.sleep(1)

        run(f"sudo mv -f {self.temporary_config_file} {self.config_file}")
        run(f"sudo rm -f {self.temporary_config_file}")

        # If there is a session running.
        # Verify that the expected configuration matches.
        # If wayland is expected from custom.conf and xorg is detected, restart the session.
        currently_running_type = None
        try:
            if os.environ["XDG_SESSION_TYPE"] == "x11":
                currently_running_type = "xorg"
            else:
                currently_running_type = os.environ["XDG_SESSION_TYPE"]
        except KeyError:
            currently_running_type = None

        # Save bool value signifying running session.
        session_is_currently_running = currently_running_type in ("xorg", "wayland")

        # Check only if session is currently running.
        # None signifies that the session is not running.
        if session_is_currently_running and (currently_running_type != self.session_type):
            self.session_restart_required = True

    def handling_account_setup(self) -> None:
        """
        Handling account setup
        """

        # Get all defined desktop file name for xorg and wayland.
        acceptable_x_desktop_names = run("ls /usr/share/xsessions").split("\n")
        acceptable_wayland_desktop_names = run("ls /usr/share/wayland-sessions").split("\n")
        acceptable_desktop_file_names = None

        # Get acceptable desktop file names for xorg.
        if self.session_type == "xorg":
            acceptable_desktop_file_names = [
                x.replace(".desktop", "") for x in acceptable_x_desktop_names if x
            ]

        # Get acceptable desktop file names for wayland.
        elif self.session_type == "wayland":
            acceptable_desktop_file_names = [
                x.replace(".desktop", "")
                for x in acceptable_wayland_desktop_names
                if x
            ]

        # Get initial values that we work with.
        interface = "".join((
            "org.freedesktop.Accounts ",
            f"/org/freedesktop/Accounts/User{self.user_id} ",
            "org.freedesktop.Accounts.User",
        ))
        saved_session_desktop = run(f"busctl get-property {interface} Session")
        saved_x_session_desktop = run(f"busctl get-property {interface} XSession")

        # Handling result from get-property. Making sure they are equal.
        saved_session_desktop = saved_session_desktop[3:-1]
        saved_x_session_desktop = saved_x_session_desktop[3:-1]
        if saved_session_desktop == "":
            run(f"busctl call {interface} SetSession 's' '{saved_x_session_desktop}'")
            saved_session_desktop = saved_x_session_desktop
        elif saved_x_session_desktop == "":
            run(f"busctl call {interface} SetXSession 's' '{saved_session_desktop}'")
            saved_x_session_desktop = saved_session_desktop

        # Chosen desktop differs from current one.
        if (
            self.session_desktop not in (saved_session_desktop, None)
            and self.session_desktop in acceptable_desktop_file_names
        ):
            print_info(f"Changing desktop '{saved_session_desktop}' -> '{self.session_desktop}'")
            run(f"busctl call {interface} SetSession 's' '{self.session_desktop}'")
            run(f"busctl call {interface} SetXSession 's' '{self.session_desktop}'")
            self.session_restart_required = True

        # Choosing desktop not found in acceptable desktop file names.
        elif (
            self.session_desktop is not None
            and self.session_desktop not in acceptable_desktop_file_names
        ):
            print_info("This is not acceptable session desktop name. Fallback to the 'gnome' session desktop")
            print_info(f"Acceptable names for '{self.session_type}': {acceptable_desktop_file_names}")

            run(f"busctl call {interface} SetSession 's' 'gnome'")
            run(f"busctl call {interface} SetXSession 's' 'gnome'")

            self.session_restart_required = True

    def handling_debug_accessibility_setup(self) -> None:
        """
        Handling debug accessibility setup.
        """

        # If there is no debug file do not attempt to set it.
        if not os.path.isfile(self.debug_a11y_file):
            return

        run(f"cp -f {self.debug_a11y_file} {self.temporary_debug_a11y_file}")

        config_parser = configparser.ConfigParser()
        # Default option returns lower-case, setting this will make it case sensitive.
        config_parser.optionxform = str
        config_parser.read(self.temporary_debug_a11y_file)

        if not config_parser.has_section("Service"):
            config_parser.add_section("Service")

        config_parser.set("Service", "Environment", '"G_MESSAGES_DEBUG=a11y-settings-plugin"')

        # Write the data to temporary file.
        with open(self.temporary_debug_a11y_file, "w", encoding="utf-8") as _file:
            config_parser.write(_file)

        if not os.path.isfile(self.temporary_debug_a11y_file):
            print_info("Temporary config file was not found, waiting a bit...")
            time.sleep(1)

        # Moving the file to its destination and removing the temporary one.
        run(f"sudo mv -f {self.temporary_debug_a11y_file} {self.debug_a11y_file}")
        run(f"sudo rm -f {self.temporary_debug_a11y_file}")

        print_info("Enabling G_MESSAGES_DEBUG for accessibility.")

    def handling_unsafe_mode_setup(self, use_unsafe_mode=True, desktop="gnome-shell") -> None:
        """
        Handling unsafe mode setup.

        :param use_unsafe_mode: Using unsafe mode, defaults to True.
        :type use_unsafe_mode: bool, optional
        """

        print_info("Handling --unsafe-mode.")

        if desktop not in ("gnome-shell", "gnome-kiosk"):
            print_info("Unknown desktop, unable to set unsafe mode.")
            return

        unsafe_config = None
        unsafe_config_etc = None
        unsafe_temporary_config = None

        if desktop == "gnome-shell":
            unsafe_config = self.unsafe_mode_config_file_shell
            unsafe_config_etc = self.unsafe_mode_config_file_shell_etc
            unsafe_temporary_config = self.temporary_unsafe_mode_config_file_shell

        if desktop == "gnome-kiosk":
            unsafe_config = self.unsafe_mode_config_file_kiosk
            unsafe_config_etc = self.unsafe_mode_config_file_kiosk_etc
            unsafe_temporary_config = self.temporary_unsafe_mode_config_file_kiosk

        # No point of checking unsafe mode of gnome-shell if there is no gnome-shell.
        #if self.session != "gnome":
        #    print_info(f"GNOME not detected at this point: session is '{self.session}'")
        #    return

        # If the gnome-shell or kiosk has no unsafe mode, do not use it.
        unsafe_mode_present = run_verbose(f"/usr/bin/{desktop} --unsafe-mode --help")
        unsafe_mode_present_output = unsafe_mode_present[0].strip("\n")
        unsafe_mode_present_return_code = unsafe_mode_present[1]
        if unsafe_mode_present_return_code != 0:
            print_info(f"Unsafe mode available?: '{unsafe_mode_present_output}'")
            return

        # Handling unsafe mode setup.
        if not os.path.isfile(unsafe_config):
            print_info("Defined unsafe mode config file not detected.")
            # File is not present on rhel-8 so it will not be executed.
            return

        if not unsafe_config or not unsafe_temporary_config:
            print_info(f"Nothing to copy: '{unsafe_config}', '{unsafe_temporary_config}'")
            return

        run(f"cp -f {unsafe_config} {unsafe_temporary_config}")

        config_parser = configparser.ConfigParser()
        config_parser.optionxform = str
        config_parser.read(unsafe_temporary_config)

        if (
            use_unsafe_mode
            and f"/usr/bin/{desktop} --unsafe-mode" not in config_parser.get("Service", "ExecStart")
        ):
            print_info(f"Using {desktop} --unsafe-mode under Wayland.")
            config_parser.set("Service", "ExecStart", f"/usr/bin/{desktop} --unsafe-mode")
            self.session_restart_required = True

        elif (
            not use_unsafe_mode
            and config_parser.get("Service", "ExecStart") != f"/usr/bin/{desktop}"
        ):
            config_parser.set("Service", "ExecStart", f"/usr/bin/{desktop}")

        # No change required.
        else:
            run(f"sudo rm -f {unsafe_temporary_config}")
            return

        with open(unsafe_temporary_config, "w", encoding="utf-8") as _file:
            config_parser.write(_file)

        move_service = run_verbose(f"sudo mv -f {unsafe_temporary_config} {unsafe_config}")

        # Check the return code.
        if move_service[1] != 0:
            print_info(move_service[2])
            print_info("Most likely running in Image Mode.")
            print_info("Using /etc/systemd/user/ directory to set --unsafe-mode.")
            move_service = run_verbose(f"sudo mv -f {unsafe_temporary_config} {unsafe_config_etc}")

        run_verbose(f"sudo rm -f {unsafe_temporary_config}")


    def handling_virtual_monitors(self) -> None:
        """
        Handling virtual monitors.
        """

        if not os.path.isfile(self.virtual_monitor_config_file):
            # End quietly in systems it is not usable.
            return

        if not os.path.isfile(self.virtual_monitor_config_file) and self.virtual_monitors:
            # End with info message in systems it is not usable and used.
            print_info("Virtual Monitors feature unavailable.")
            return

        run(f"cp -f {self.virtual_monitor_config_file} {self.temporary_virtual_monitor_config_file}")

        config_parser = configparser.ConfigParser()
        config_parser.optionxform = str
        config_parser.read(self.temporary_virtual_monitor_config_file)

        # Add a virtual monitor with default size, configurable in session.
        virtual_monitor_string = " --virtual-monitor 1024x768"

        service_exec = config_parser.get("Service", "ExecStart")

        lm_occurrences = service_exec.count(virtual_monitor_string)
        # If there are occurrences found and user wants zero. Remove all virtual monitors.
        if lm_occurrences > 0 and self.virtual_monitors == 0:
            print_info("Removing virtual monitors.")
            config_parser.set(
                "Service",
                "ExecStart",
                service_exec.replace(virtual_monitor_string, "")
            )
            self.session_restart_required = True


        elif lm_occurrences != self.virtual_monitors:
            print_info(f"Adding {self.virtual_monitors} virtual monitor/s with resolution 1024x768.")
            config_parser.set(
                "Service",
                "ExecStart",
                service_exec.replace(virtual_monitor_string, "") + virtual_monitor_string * self.virtual_monitors
            )
            self.session_restart_required = True

        # No change required.
        else:
            run(f"sudo rm -f {self.temporary_virtual_monitor_config_file}")
            return

        with open(self.temporary_virtual_monitor_config_file, "w", encoding="utf-8") as _file:
            config_parser.write(_file)

        run(f"sudo mv -f {self.temporary_virtual_monitor_config_file} {self.virtual_monitor_config_file}")
        run(f"sudo rm -f {self.temporary_virtual_monitor_config_file}")


    def start_display_manager(self) -> None:
        """
        Starting the display manager.
        """

        # Stop display manager only if requested by user or required by configuration change.
        # Continue using the running session otherwise.
        if self.display_manager_restart or self.session_restart_required:
            print_info("Restart required.")

            # Stopping display manager to reload session type.
            self.stop_display_manager()
            # A little delay to prevent races.
            time.sleep(1)

        list_of_systemd_processes = (
            run(f"pgrep -u {os.geteuid()} -f '/usr/lib/systemd/systemd --user'")
            .strip("\n")
            .split("\n")
        )
        number_of_systemd_processes = len(list_of_systemd_processes)

        if number_of_systemd_processes > 1:
            print_info("Multiple instances of '/usr/lib/systemd/systemd --user' detected - trying to recover...")

            # Stop the running session first - important for 'keep' option.
            self.stop_display_manager()

            for pid in list_of_systemd_processes:
                run(f"sudo kill -9 {pid}")

            # Prevent any race when cleaning systemd processes and starting display manager.
            time.sleep(1)


        # Example loginctl show-user 1000 --property=Sessions with run_verbose.
        # ("Sessions=X Y", <return_code>, <error_message>)
        loginctl_command = f"loginctl show-user {self.user} --property=Sessions"
        loginctl_show_user_sessions_verbose = run_verbose(loginctl_command)

        # If the command return code is 0 we can assume it has the data we need.
        if loginctl_show_user_sessions_verbose[1] == 0:
            # Get the actual command output.
            loginctl_show_user_sessions_output = loginctl_show_user_sessions_verbose[0]

            # "Sessions=X Y" -> ["Sessions", "X Y"]
            sessions_list = loginctl_show_user_sessions_output.split("=", 1)

            # Initiating the session number list.
            session_numbers_list = []
            # Get the data only if it is in expected format.
            if len(sessions_list) == 2:
                # ["Sessions", "X Y"] -> "X Y"
                session_numbers_string = sessions_list[1]
                # "X Y" -> ["X", "Y"]
                session_numbers_list = session_numbers_string.split(" ")

            for session in session_numbers_list:
                if not session.isdigit():
                    # No session detected, skipping.
                    break

                # In case of unforeseen issues, initiate the values.
                session_type = ""
                session_service = ""

                # Sessions are numbers X, Y, ..
                session_type_command = f"loginctl show-session {session} --property=Type"
                session_type_verbose = run_verbose(session_type_command)
                if session_type_verbose[1] == 0:
                    # Expected type output is Type=x11 or Type=wayland
                    session_type = session_type_verbose[0].split("=", 1)[1]

                # Sessions are numbers X, Y, ..
                session_service_command = f"loginctl show-session {session} --property=Service"
                session_service_verbose = run_verbose(session_service_command)
                if session_service_verbose[1] == 0:
                    # Expected service output is Service=gdm-autologin
                    session_service = session_service_verbose[0].split("=", 1)[1]

                # For easy readability, adding bool function which is not needed.
                expected_type = bool(session_type in ("x11", "wayland"))
                expected_service = bool("autologin" in session_service)

                # Have a variable to check if a session was detected in closing state.
                session_in_closing_state = False

                # If both conditions apply check the State of the session.
                if expected_type and expected_service:

                    # If something goes wrong the system might hang up to 90 seconds
                    # waiting for the service to die.
                    for _ in range(100):
                        # Reload the variable.
                        loginctl_command = f"loginctl show-session {session} --property=State"
                        session_state = run(loginctl_command).strip("\n")

                        # Make the check for the state and act properly.
                        if session_state == "State=closing":
                            session_in_closing_state = True
                            time.sleep(1)

                        elif session_state == "State=active":
                            break

                # If closing state was detected and it got to this point.
                # The session is still closing, kill it.
                if session_in_closing_state:
                    print_info("".join((
                        "Session detected in closing state ",
                        "which did not end after 100 seconds, sending SIGTERM."
                    )))
                    time.sleep(1)

                    # Extra log straight to journal if for some reason wrong session is killed.
                    log_message_to_journal(
                        priority="warning",
                        identifier="dogtail-headless",
                        invoke=f"echo '=== loginctl kill-session --signal=15 {session} ==='"
                    )

                    run(f"sudo loginctl kill-session --signal=15 {session}")
                    time.sleep(1)


        # Start display manager if display manager is not active already.
        is_display_manager_active = run(f"systemctl is-active {self.display_manager}").strip("\n")
        if is_display_manager_active != "active":
            run(f"sudo systemctl start {self.display_manager}")
            print_info("Starting Display Manager.")

            time.sleep(4)

        # But the session must be running.
        if not self.wait_until_process_is_running(self.session_started_indicator):
            print_info(" ".join((
                f"Running session indicator '{self.session_started_indicator}'",
                "was not detected - restart required."
            )))
            print_info(f"Attempt to restore headless - stopping '{self.display_manager}'")
            self.stop_display_manager()
            print_info(f"Attempt to restore headless - starting '{self.display_manager}'")
            run(f"sudo systemctl start {self.display_manager}")
            time.sleep(4)


    def stop_display_manager(self) -> None:
        """
        Stopping the display manager.
        """

        run(f"sudo systemctl stop {self.display_manager}")
        print_info("Stopping Display Manager.")

        # Dumb sleep to prevent any kind of races.
        time.sleep(3)

        self.wait_until_process_is_not_running(self.session_started_indicator)

        # Failsafe, the session should end, but if not
        # send SIGTERM and give it time to close.
        loginctl_command = f"sudo loginctl | grep {self.user} | grep seat0"
        still_open_session = run_verbose(loginctl_command)
        # Check return code.
        if still_open_session[1] == 0:
            os.system("sudo loginctl")

            still_open_session_number = (
                run(f"sudo loginctl | grep {self.user} | grep seat0")
                .strip(" ")
                .split(" ")[0]
            )
            print_info(f"Session did not end after 'systemctl stop {self.display_manager}'.")
            print_info(f"Sending SIGTERM to '{still_open_session_number}'.")
            time.sleep(1)

            # Extra log straight to journal if for some reason wrong session is killed.
            log_message_to_journal(
                priority="warning",
                identifier="dogtail-headless",
                invoke=f"echo '=== loginctl kill-session --signal=15 {still_open_session_number} ==='"
            )

            run(f"sudo loginctl kill-session --signal=15 {still_open_session_number}")
            time.sleep(1)

            # If something goes wrong the system might hang up to 90 seconds waiting
            # for the service to die.
            for counter in range(100):
                loginctl_command = f"loginctl show-user {self.user} --property=State"
                user_still_logged_in = run_verbose(loginctl_command)
                user_still_logged_in_stripped = user_still_logged_in[0].strip("\n")
                if user_still_logged_in_stripped == "State=closing":
                    print_info(f"State of '{loginctl_command}' is '{user_still_logged_in_stripped}'.")
                    time.sleep(1)

                elif user_still_logged_in_stripped == "State=active":
                    print_info("Session is still active after sending SIGTERM.")
                    break

                # Failed to get user: User ID 1000 is not logged in or lingering.
                elif user_still_logged_in[1] == 1:
                    print_info(f"Session ended after SIGTERM in '{counter}' seconds.")
                    break

        # Leftover display manager process that seems to mess everything up.
        still_open_dm_session = run_verbose(f"sudo loginctl | grep {self.display_manager}")

        # Check return code.
        if still_open_dm_session[1] == 0:
            os.system("sudo loginctl")

            still_open_dm_session_number = run(f"sudo loginctl | grep {self.display_manager}").strip(" ").split(" ")[0]
            print_info(f"Session still open, sending SIGTERM to '{self.display_manager}' login '{still_open_dm_session_number}'.")
            time.sleep(1)

            # Extra log straight to journal if for some reason wrong session is killed.
            log_message_to_journal(
                priority="warning",
                identifier="dogtail-headless",
                invoke=f"echo '=== loginctl kill-session --signal=15 {still_open_dm_session_number} ==='"
            )

            run(f"sudo loginctl kill-session --signal=15 {still_open_dm_session_number}")
            time.sleep(1)


    @staticmethod
    def is_process_running(process_to_find) -> bool:
        """
        Is process running helper function.

        :param process_to_find: Process to find.
        :type process_to_find: str

        :return: Process is running.
        :rtype: bool
        """

        active_processes = run("ps axw").split("\n")
        for active_process in active_processes:
            if re.search(process_to_find, str(active_process).lower()):
                return True
        return False

    def wait_until_process_is_running(self, process_to_find) -> bool:
        """
        Waiting until the process is running function.

        :param process_to_find: Process to find.
        :type process_to_find: str

        :return: The process was found before the 30 second timeout.
        :rtype: bool
        """

        for _ in range(60):
            if not self.is_process_running(process_to_find):
                time.sleep(0.5)
            else:
                return True
        return False

    def wait_until_process_is_not_running(self, process_to_find) -> None:
        """
        Waiting until the process is NOT running function.

        :param process_to_find: Process to NOT find.
        :type process_to_find: str

        :return: The process was NOT found in the 30 second timeout.
        :rtype: bool
        """

        for _ in range(60):
            if self.is_process_running(process_to_find):
                time.sleep(0.5)
            else:
                break


class Headless:
    """
    Headless class.
    """

    def __init__(self) -> None:
        # Saving journal cursor for debugging.
        initial_cursor_output = run("sudo journalctl --lines=0 --show-cursor").strip()
        cursor_target = initial_cursor_output.split("cursor: ", 1)[-1]
        self.logging_cursor = f'"--after-cursor={cursor_target}"'

        self.display_manager_control = None
        self.environment_control = None
        self.script_control = None

        self.arguments = None
        self.script_as_list_of_arguments = ""

        self.session = None
        self.session_binary = None
        self.display_manager = None

        self.enable_start = True
        self.enable_stop = True

        self.display_manager_restart = False

        self.disable_accessibility_on_script_exit = None

        self.force = None
        self.session_type = None
        self.session_desktop = None

        self.user_script_process = None
        self.user_script_exit_code = None

        self.no_automatic_login = False

        self.display_number = ":0"
        self.virtual_monitors = 0

        self.allow_duplication = False

        self.term = None

        # Upon configuration change restart the session if it is running.
        self.restart_required = False

    @staticmethod
    def set_accessibility_to(enable_accessibility) -> None:
        """
        Using simple gsettings command to enable or disable toolkit-accessibility.
        """

        set_accessibility_value = "true" if enable_accessibility else "false"

        gsetting_get_command = " ".join(
            (
                "dbus-run-session gsettings get",
                "org.gnome.desktop.interface",
                "toolkit-accessibility",
            )
        )

        gsetting_set_command = " ".join(
            (
                "dbus-run-session gsettings set",
                "org.gnome.desktop.interface",
                f"toolkit-accessibility {set_accessibility_value}",
            )
        )

        accessibility_value = run(gsetting_get_command)
        if accessibility_value != set_accessibility_value:
            print_info(f"Changing a11y value from '{accessibility_value}' to '{set_accessibility_value}'")
            run(gsetting_set_command)

    @staticmethod
    def adjust_gsettings_values() -> None:
        """
        Using simple gsettings command to adjust values of delay, repeat and repeat-interval.
        """

        user = run("whoami")
        scheme = "org.gnome.desktop.peripherals.keyboard"

        gsetting_get_delay_command = f"sudo -Hu {user} gsettings get {scheme} delay"
        gsetting_set_delay_command = f"sudo -Hu {user} gsettings set {scheme} delay 'uint32 500'"

        gsetting_get_repeat_command = f"sudo -Hu {user} gsettings get {scheme} repeat"
        gsetting_set_repeat_command = f"sudo -Hu {user} gsettings set {scheme} repeat true"

        gsetting_get_repeat_interval_command = f"sudo -Hu {user} gsettings get {scheme} repeat-interval"
        gsetting_set_repeat_interval_command = f"sudo -Hu {user} gsettings set {scheme} repeat-interval 'uint32 30'"

        delay_result = run(gsetting_get_delay_command)
        repeat_result = run(gsetting_get_repeat_command)
        repeat_interval_result = run(gsetting_get_repeat_interval_command)

        if delay_result != "uint32 500":
            run(gsetting_set_delay_command)
            print_info(f"Value of gsettings delay was '{delay_result}' - changing to 'uint32 500'.")

        if repeat_result != "true":
            run(gsetting_set_repeat_command)
            print_info(f"Value of gsettings repeat was '{repeat_result}' - changing to 'true'.")

        if repeat_interval_result != "uint32 30":
            run(gsetting_set_repeat_interval_command)
            print_info(f"Value of gsettings repeat-interval was '{repeat_interval_result}' - changing to 'uint32 30'.")

    def troubleshoot(self) -> None:
        """
        Test parts of the system for correct configuration.
        """

        # Troubleshooting gnome-session-binary upon failure.
        user_id = str(os.geteuid())
        gnome_session_binary_pid = run(f"pgrep -fAu {user_id} {self.session_binary}").split("\n")[0]
        ps_command = f"ps ax -o uid,gid,pid,tname,command | grep {self.session_binary}"
        ps_command_result = run(ps_command)

        print_info(f"Troubleshooting '{self.session_binary}':")
        print(f"Target file for environment is '{self.session_binary}'")
        print(f"Search was done with 'pgrep -fAu {user_id} {self.session_binary}'.")
        print(f"With result '{str(gnome_session_binary_pid)}'\n")

        print_info("Actual running processes:")
        print(f"$ {ps_command}")
        print(f"{str(ps_command_result)}\n")

        # Troubleshooting dbus upon failure.
        dbus_processes_command = "ps ax -o uid,gid,pid,tname,command | grep dbus"
        dbus_processes_result = run(dbus_processes_command)
        print_info("Troubleshooting dbus:")
        print(f"$ {dbus_processes_command}")
        print(f"{dbus_processes_result}\n")

        # Troubleshooting at-spi processes that are required.
        print_info("Troubleshooting AT-SPI processes:")
        at_spi_command = "ps ax -o uid,gid,pid,tname,command | grep at-spi"
        at_spi_result = run(at_spi_command)
        print_info("Expecting running processes to be:")
        print("'/usr/libexec/at-spi-bus-launcher'")
        print("'/usr/libexec/at-spi2-registryd'\n")

        print_info("Actual running processes:")
        print(f"$ {at_spi_command}")
        print(f"{at_spi_result}\n")

        # Troubleshooting important environment variables.
        print_info("Troubleshooting Environment variables:")
        display = os.getenv("DISPLAY")
        xauthority = os.getenv("XAUTHORITY")
        dbus_session_bus_address = os.getenv("DBUS_SESSION_BUS_ADDRESS")
        print(f"DISPLAY = '{display}'")
        print(f"XAUTHORITY = '{xauthority}'")
        print(f"DBUS_SESSION_BUS_ADDRESS = '{dbus_session_bus_address}'\n")


        session_result = "ps ax | grep -E 'gdm|gnome-shell|gnome-session'"
        session_run_result = run(session_result)
        print(f"SESSION DEBUG:\n'{session_run_result}'")

        journal_run = run_verbose(" ".join((
            "sudo journalctl --all",
            f"--output=short-precise {self.logging_cursor}",
            f"| grep -E '{self.display_manager}|gnome-shell|gnome-session'",
        )))

        if journal_run[1] != 0:
            print_info(f"journalctl data gathering failed: '{journal_run}'")
        else:
            print_info("journalctl data:")
            print(f"{journal_run[0]}\n")

    def handle_keep_logic(self, keep_value) -> None:
        """
        Handling keep logic.

        :param keep_value: String form of an integer expressing how many test will be
            run in a single session before restart.
        :type keep_value: str
        """

        keep_file = "/tmp/dogtail_keep"
        keep_from_argument = int(keep_value)

        try:
            with open(keep_file, "r", encoding="utf-8") as _file:
                keep_from_file = int(_file.read())
        except OSError:
            keep_from_file = 1

        self.enable_stop = False

        if keep_from_file == 1:
            self.display_manager_restart = True

        if keep_from_file >= keep_from_argument:
            self.enable_stop = True
            keep_from_file = 0

        with open(keep_file, "w", encoding="utf-8") as _file:
            _file.write(f"{keep_from_file + 1}")

    def handle_arguments(self) -> None:
        """
        Makes all necessary steps for arguments passed along the headless script.
        """

        # Workaround for firefox with bugged accessibility which will sometimes turn off.
        os.environ["GNOME_ACCESSIBILITY"] = "1"

        # Parse arguments of headless.
        self.arguments = parse()

        # Parse arguments of given script.
        self.script_as_list_of_arguments = self.arguments.script.split()

        # Handle session.
        if self.arguments.session:
            self.session = self.arguments.session

        # Handle session binary.
        if self.arguments.session_binary:
            self.session_binary = self.arguments.session_binary

        # Handle display manager.
        if self.arguments.dm:
            self.display_manager = self.arguments.dm

        # Default session / binary logic.
        if self.display_manager == "lightdm":
            self.session = self.session or "mate"
            self.session_binary = self.session_binary or "/usr/bin/mate-session"

        elif self.display_manager == "sddm":
            self.session = self.session or "kde"
            self.session_binary = self.session_binary or "/usr/bin/plasmashell"

        elif self.display_manager in (None, "gdm"):
            self.display_manager = "gdm"
            self.session_binary = self.session_binary or "/usr/bin/gnome-session"

        else:
            print(f"Unknown Display Manager '{self.display_manager}'!")
            sys.exit(-1)

        # If there is no default, user needs to specify.
        if not self.session_binary:
            print_info(f"Need to specify --session-binary for '{self.session}'.")
            sys.exit(-1)

        # Handle headless duplication.
        if self.arguments.allow_duplication:
            self.allow_duplication = True

        # Handle headless debug variable.
        if self.arguments.debug:
            os.environ["DOGTAIL_DEBUG"] = "true"

        # Handle keep argument, check value of /tmp/dogtail_keep.
        if self.arguments.keep:
            self.handle_keep_logic(self.arguments.keep)

        # Handle display number.
        if self.arguments.display:
            self.display_number = self.arguments.display

        # Handle headless don't start variable.
        if self.arguments.dont_start:
            self.enable_start = False

        # Handle headless don't kill variable.
        # Handle headless keep max variable, which is just do not kill variable.
        if self.arguments.dont_kill or self.arguments.keep_max:
            self.enable_stop = False

        # Handle headless restart variable.
        if self.arguments.restart:
            self.display_manager_restart = True

        # Handle headless disable a11y variable.
        if self.arguments.disable_a11y:
            self.disable_accessibility_on_script_exit = True

        # Handle headless force variable.
        if self.arguments.force:
            self.force = True

        # Handle session type variable.
        if self.arguments.session_type:
            self.session_type = self.arguments.session_type

        # Handle session desktop variable.
        if self.arguments.session_desktop:
            self.session_desktop = self.arguments.session_desktop

        # Handle no automatic login variable.
        if self.arguments.no_autologin:
            self.no_automatic_login = self.arguments.no_autologin

        # Handle TERM variable.
        if self.arguments.term:
            self.term = self.arguments.term

    def set_display_number(self) -> None:
        """
        Retrieve information about running process and prints it before user script start.
        """

        os.environ["DISPLAY"] = self.display_number
        print_info(f"Setting DISPLAY variable to '{self.display_number}'.")

    def check_what_desktop_and_type_is_running(self) -> None:
        """
        Retrieve information about running process and prints it before user script start.
        """

        if not self.enable_start:
            return

        error_list = []
        try:
            if os.environ["XDG_SESSION_TYPE"] == "x11":
                current_type = "xorg"
            else:
                current_type = os.environ["XDG_SESSION_TYPE"]

        except KeyError as error:
            error_list.append(error)
            current_type = "__unavailable__"

        try:
            current_desktop = os.environ["XDG_SESSION_DESKTOP"]
        except KeyError as error:
            error_list.append(error)
            current_desktop = "__unavailable__"

        print_info(f"Running '{current_type}' with desktop '{current_desktop}'")

        if error_list:
            print_info(f"Error detected when loading environment variables: '{error_list}'")

    def verify_that_correct_session_was_started(self) -> None:
        """
        Verifies that correct session type as started, terminate on mismatch.
        """

        if not self.enable_start:
            return

        # Using 'xorg' naming for x11 session.
        current_type = ""
        if os.environ["XDG_SESSION_TYPE"] == "x11":
            current_type = "xorg"
        else:
            current_type = os.environ["XDG_SESSION_TYPE"]

        if (
            self.display_manager_control.session_type
            and self.display_manager_control.session_type != current_type
        ):
            print_info(f"Script requires session of type: '{self.display_manager_control.session_type}'")
            print_info(f"Script was started under session of type: '{current_type}'\n")

            # Check if the session failed because of drivers.
            # Actual use case is to know if wayland failed because of qxl driver.
            for command in ["lspci", "sudo lspci"]:
                # Execute the lspci command and check if it was a success.
                lspci_result = run_verbose(command)
                if lspci_result[1] == 0:
                    # On success print the result and skip to the headless exit.
                    print_info(f"'{command}' command output:\n{lspci_result[0]}")
                    break
                # On fail print the error and run the 'sudo lspci' command.
                print_info(f"'{command}' command did not succeed: '{lspci_result}'.")

            print_info("Exiting the headless script.")
            sys.exit(1)

        current_desktop = os.environ["XDG_SESSION_DESKTOP"]
        if (
            self.display_manager_control.session_desktop
            and self.display_manager_control.session_desktop != current_desktop
        ):
            print_info(f"Script requires session with desktop: '{self.display_manager_control.session_desktop}'")
            print_info(f"Script was started under session with desktop: '{current_desktop}'\n")
            print_info("Exiting the headless script.")
            sys.exit(1)

    def handle_coloring_of_headless_messages(self, use_color=True) -> None:
        """
        Handle coloring of headless images.
        """

        # Process id of current (headless) process - os.getpid()
        # Process group id of current (headless) process - os.getpgid(0)
        # If they differ, the process (headless) was started from another script.
        # Another option is to check if real terminal is used and enable nested starts
        # also. Serves as an indicator if we can use colors or not.

        global COLORS_ENABLED

        # User cmd line arguments has top priority.
        if not use_color:
            COLORS_ENABLED = False
            print("headless: Colors disabled by user.")

        # Next priority is isatty or if the script was started directly.
        elif sys.stdout.isatty() or os.getpid() == os.getpgid(0):
            COLORS_ENABLED = True
            print_info("Colors enabled.")

        # In other cases just disable the colors.
        else:
            print("headless: Colors disabled.")

    def handle_nested_dogtail_process(self):
        """
        Handle nested dogtail headless process.
        """

        # First lets make sure no orphaned processes are present.
        cmd = ["pgrep -f .*dogtail-headless*"]
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )
        all_dogtail_processes, _ = process.communicate()
        all_dogtail_processes = all_dogtail_processes.splitlines()

        try:
            # Import psutil here in case it is missing on the system.
            import psutil

            # Iterate over processes.
            for process_id in all_dogtail_processes:
                # Get parent_process_id from process_id.
                try:
                    parent_process_id = psutil.Process(int(process_id)).ppid()
                except Exception:
                    pass

                # Orphaned dogtail-headless check, terminate it.
                if int(parent_process_id) == 1:
                    print_info(f"Terminating orphaned '{process_id}' dogtail-headless process.")
                    run(f"sudo kill -15 {process_id}")
                    time.sleep(1)

        except ImportError:
            print_info("Module 'psutil' unavailable. Any orphaned process is not terminated.")

        except TypeError as error:
            print_info(f"Attempted to use PID that is not valid: '{error}'.")
            print_info(f"Process IDs used: '{all_dogtail_processes}'.")

        # Failsafe if user wants to start another nested script.
        cmd = ["pgrep -f .*python.*dogtail-headless*"]
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )
        all_dogtail_processes, _ = process.communicate()

        number_of_running_python_headless_scripts = len(all_dogtail_processes.splitlines())
        if number_of_running_python_headless_scripts > 1:
            print_info("Attempting to start another instance of headless script.")
            print_info("Exiting the duplicate of headless script.")
            sys.exit(1)

    def execute(self) -> None:
        """
        Makes all necessary preparations for the system to start display manager and
        execute user script.
        """

        # Arguments handling.
        self.handle_arguments()

        try:
            from importlib.metadata import version
            dogtail_version = version("dogtail")
            print_info(f"Version of dogtail installed: '{dogtail_version}'.")
        except Exception as error:
            print_info(f"Version of dogtail was not retrieved for: '{error}'.")

        # Starting the timer to help debug issues with timeouts.
        starting_point = time.time()
        print_info("Starting the timer for the headless script.")

        # Headless is not supposed to be run under user root.
        if os.geteuid() == 0:
            print_info("Script is not meant to be run under the root user.")
            print_info("Exiting the headless script.")
            sys.exit(1)

        # There is a bug in which the root takes ownership of dconf file. So far we did
        # not discover the cause. We can easily fix this by deleting the file, upon
        # session start new file with correct owner is created.
        verify_file_ownership()

        # Nested script handling.
        if not self.allow_duplication:
            self.handle_nested_dogtail_process()

        # Before the Display Manager handling, check if the session is running already.
        environment_dictionary = get_initial_environment_dictionary(binary=self.session_binary)
        if environment_dictionary:
            os.environ = environment_dictionary

        # Display manager setup and handling.
        print_info(f"Using Display Manager: '{self.display_manager}'")
        self.display_manager_control = DisplayManager(
            session=self.session,
            session_binary=self.session_binary,
            display_manager=self.display_manager,
            session_type=self.session_type,
            session_desktop=self.session_desktop,
            enable_start=self.enable_start,
            enable_stop=self.enable_stop,
            display_manager_restart=self.display_manager_restart,
            no_automatic_login=self.no_automatic_login,
            virtual_monitors=self.virtual_monitors
        )
        self.display_manager_control.handling_config_setup()
        self.display_manager_control.handling_account_setup()

        # Debugging a11y randomly turning off.
        self.display_manager_control.handling_debug_accessibility_setup()

         # GNOME Shell is default - when session_desktop is not provided we assume GNOME Shell is desired.
        if not self.display_manager_control.session_desktop:
            self.display_manager_control.handling_unsafe_mode_setup(
                use_unsafe_mode=(self.display_manager_control.session_type == "wayland"),
                desktop="gnome-shell"
            )

        # Set unsafe mode only for wayland and GNOME Kiosk.
        elif "kiosk" in self.display_manager_control.session_desktop:
            self.display_manager_control.handling_unsafe_mode_setup(
                use_unsafe_mode=("wayland" in self.display_manager_control.session_type),
                desktop="gnome-kiosk"
            )

        # Set unsafe mode only for wayland and GNOME Shell.
        elif "gnome" in self.display_manager_control.session_desktop:
            self.display_manager_control.handling_unsafe_mode_setup(
                use_unsafe_mode=(self.display_manager_control.session_type == "wayland"),
                desktop="gnome-shell"
            )

        else:
            print_info(f"Unexpected session desktop: '{self.display_manager_control.session_desktop}'")
            print_info("Failed to establish desktop environment, unsafe mode not set!")

        # Set virtual monitors if user requires.
        self.display_manager_control.handling_virtual_monitors()

        # Required setup that needs to go through in its entirety or it will fail.
        if self.enable_start:
            self.display_manager_control.start_display_manager()

        # Environment handling.
        environment_dictionary = get_environment_dictionary(binary=self.session_binary, term=self.term)
        if environment_dictionary:
            os.environ = environment_dictionary
        else:
            print_info("Display Manager Status is:")
            print(f"{run(f'systemctl status {self.display_manager}')}")
            self.troubleshoot()

            print_info("Attempt to retrieve environmental variables failed.")
            self.display_manager_control.stop_display_manager()
            print_info("Exiting the headless script.")
            sys.exit(1)

        # Force xorg/wayland setting - terminate upon error.
        if self.force:
            self.verify_that_correct_session_was_started()

        # Check xorg/wayland setting - print what the test will run under.
        self.check_what_desktop_and_type_is_running()

        # Set DISPLAY number.
        self.set_display_number()

        # Accessibility - has to be started after display manager / dbus is running.
        self.set_accessibility_to(True)

        # Make a gsettings that sometimes get set too high and is uncomfortable to work with.
        self.adjust_gsettings_values()

        # User script handling.
        if is_binary_existing_and_executable(self.script_as_list_of_arguments[0]):
            self.user_script_process = subprocess.Popen(
                self.script_as_list_of_arguments, env=os.environ
            )
            print_info(f"Started the script with PID {self.user_script_process.pid}.")

            self.user_script_exit_code = self.user_script_process.wait()
            return_code_string = f"The user script finished with return code {self.user_script_exit_code}."
            if int(self.user_script_exit_code) == 0:
                print_info(return_code_string)
            else:
                print_info(return_code_string)

        # Disable accessibility upon script exit.
        if self.disable_accessibility_on_script_exit:
            self.set_accessibility_to(False)

        # Stop display manager unless user specifies otherwise.
        if self.enable_stop or self.user_script_exit_code != 0:
            self.display_manager_control.stop_display_manager()

        ending_point = time.time()
        print_info(f"The headless script ran for {(ending_point - starting_point):.2f} seconds.")


def log_message_to_journal(priority, identifier, invoke):
    """
    Invoke a program to be logged in journal.

    :param priority: Priority of the message.
    :type priority: str

    :param identifier: Identifier we want in the journal.
    :type identifier: str

    :param invoke: Invoke a program to execute.
    :type invoke: str
    """

    # journal entry -p priority -t identifier [invoke a program]
    run(
        " ".join(
            (
                "systemd-cat",
                f"-p {priority}",
                f"-t {identifier}",
                invoke,
            )
        )
    )


# Graceful exit in the event of an interrupt from user SIGINT or system SIGTERM.
def graceful_exit(signum, frame):  # pylint: disable=unused-argument
    """
    Attempting graceful exit on signal interruption.
    """

    print_info(f"The headless script was interrupted by signal '{signum}'.")

    # Attempt to debug issues upon timeout if used together with qecore library.
    if int(signum) == 15 and os.path.exists("/tmp/qecore_logger.log"):
        run("echo '===== Timeout - debugging =====' >> /tmp/automation_debug.log")
        run("cat '/tmp/qecore_logger.log' >> /tmp/automation_debug.log")
        run("echo '===============================' >> /tmp/automation_debug.log")

    log_message_to_journal(
        priority="info",
        identifier="dogtail-headless",
        invoke="echo '=== Graceful exit of dogtail-headless upon SIGINT or SIGTERM ==='"
    )

    sys.exit(signum)


def main():
    """
    Main function.
    """

    log_message_to_journal(
        priority="warning",
        identifier="dogtail-headless",
        invoke="echo '=== Starting dogtail-headless ==='"
    )

    headless = Headless()

    # Register signal handlers.
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    headless.execute()

    log_message_to_journal(
        priority="warning",
        identifier="dogtail-headless",
        invoke=f"echo '=== Exiting dogtail-headless with {headless.user_script_exit_code} ==='"
    )

    sys.exit(headless.user_script_exit_code)


if __name__ == "__main__":
    main()
