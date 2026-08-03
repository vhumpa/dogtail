"""
Private a11y bus and a bare mutter, per test, with no desktop session involved.

One session per process. Libatspi caches its desktop connection in C on first
use, so a second session hands back the first one's dead objects instead of
raising.

Boot order matters: a11y bus, registryd, wait for the name, mutter, app.
"""

import ctypes
import os
import shutil
import signal
import subprocess
import tempfile
import time
import warnings

from dogtail.config import config
from dogtail.utils import do_delay


REGISTRY_NAME = "org.a11y.atspi.Registry"
REMOTE_DESKTOP_NAME = "org.gnome.Mutter.RemoteDesktop"

# Registryd is not on $PATH, it gets found by REGISTRYD_PATHS below.
REQUIRED_BINARIES = ("dbus-daemon", "dbus-send", "mutter")

REGISTRYD_PATHS = (
    "/usr/lib/at-spi2-registryd",                # Arch.
    "/usr/libexec/at-spi2-registryd",            # Fedora, RHEL.
    "/usr/lib/at-spi2-core/at-spi2-registryd",   # Debian, Ubuntu.
)

PR_SET_PDEATHSIG = 1

# Seconds. A loaded CI runner blows through anything tighter. Wait_for_app gets 3x this.
DEFAULT_TIMEOUT = float(os.environ.get("DOGTAIL_HERMETIC_TIMEOUT", "10.0"))

# Resolved at import, not in the child: after fork() only async-signal-safe
# calls are allowed, and dlopen is not one. See _die_with_parent.
_LIBC = ctypes.CDLL("libc.so.6", use_errno=True)

_booted_in_this_process = False


class HermeticSessionError(RuntimeError):
    """
    Raised for every failure a hermetic session can produce.
    """


class CoordinatesUnavailable(HermeticSessionError):
    """
    Raised when a click by coordinates would land somewhere else.
    """


def _find_registryd():
    """
    Locate the at-spi2-registryd binary.

    :raises HermeticSessionError: Registryd is in none of the known locations.

    :return: Path to the registryd binary.
    :rtype: str
    """

    override = os.environ.get("DOGTAIL_REGISTRYD")
    if override:
        return override

    for path in REGISTRYD_PATHS:
        if os.path.exists(path):
            return path

    raise HermeticSessionError(
        f"at-spi2-registryd not found in {REGISTRYD_PATHS}; "
        "set $DOGTAIL_REGISTRYD to its path"
    )


def missing_binaries():
    """
    List what a session needs and cannot find.

    Public so that tests can hang a skipIf on it.

    :return: Names of the binaries that are not installed.
    :rtype: list(str)
    """

    missing = [name for name in REQUIRED_BINARIES if shutil.which(name) is None]
    try:
        _find_registryd()
    except HermeticSessionError:
        missing.append("at-spi2-registryd")

    return missing


def _check_binaries():
    """
    Say what is missing up front, rather than letting subprocess raise later.

    :raises HermeticSessionError: At least one required binary is missing.
    """

    missing = missing_binaries()
    if not missing:
        return

    raise HermeticSessionError(
        f"a hermetic session needs {', '.join(missing)}, and can't find "
        f"{'them' if len(missing) > 1 else 'it'}. dbus-daemon and dbus-send "
        f"ship as dbus and dbus-tools, at-spi2-registryd as at-spi2-core "
        f"(set $DOGTAIL_REGISTRYD if your distro puts it somewhere else than "
        f"{REGISTRYD_PATHS})."
    )


def _die_with_parent():
    """
    Ask the kernel to terminate this child once its parent is gone.

    SIGKILL the test runner and teardown never runs, which leaves mutter behind.

    This is the preexec_fn of subprocess, which Python's own documentation calls
    unsafe with threads. The hazard is cut down to size: the libc handle is
    resolved at import time, so all that happens here is one already-resolved
    syscall. A pidfd does not cover this case, it tells a parent about a dead
    child rather than the other way round.
    """

    _LIBC.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)


def _check_first_session():
    """
    Refuse a second session in the same process.

    Libatspi hands back the first session's dead objects and reports
    childCount=-1 rather than raising, so the test sees an empty desktop and no
    reason why. Only a session that came up counts, a failed boot never touched
    libatspi.

    :raises HermeticSessionError: A session already booted in this process.
    """

    if _booted_in_this_process:
        raise HermeticSessionError(
            "a HermeticSession already booted in this process. libatspi caches "
            "its desktop connection in C on first use, so a second session "
            "silently talks to the first one's dead bus (childCount=-1, no "
            "exception). Run one session per process: setUpClass in unittest, "
            "or the session-scoped fixture in dogtail.hermetic.fixtures."
        )


class HermeticSession:
    """
    A private session made of a bus, a registry and a headless compositor.

    The XDG_* variables point at a temporary directory so that the application
    under test cannot see the host configuration. They are exported into
    os.environ as well, since dogtail.tree binds root at import time and would
    otherwise grab the host's bus.

    One bus carries both a11y and mutter. Split it if anything else ever joins.
    """

    def __init__(self, virtual_monitor="1280x1024", boot_timeout=None):
        """
        Prepare a session. Nothing is started until boot() is called.

        :param virtual_monitor: Resolution to give mutter, defaults to "1280x1024"
        :type virtual_monitor: str, optional

        :param boot_timeout: Seconds to wait for each service, defaults to
            $DOGTAIL_HERMETIC_TIMEOUT or 10.0
        :type boot_timeout: float, optional
        """

        self.virtual_monitor = virtual_monitor
        self.boot_timeout = DEFAULT_TIMEOUT if boot_timeout is None else boot_timeout

        self.temporary_root = None
        self.bus_address = None
        self.wayland_display = "wayland-0"
        self.environment = None

        self._dbus_process = None
        self._registryd_process = None
        self._mutter_process = None
        self._logs = {}
        self._saved_environment = None

    def __enter__(self):
        """
        Boot the session on entering the context.

        :return: The environment the session runs in.
        :rtype: dict(str, str)
        """

        return self.boot()

    def __exit__(self, exception_type, exception, exception_traceback):
        """
        Tear the session down on leaving the context.

        :return: False, so that any exception keeps propagating.
        :rtype: bool
        """

        self.teardown()

        return False

    def boot(self):
        """
        Start the bus, the registry and the compositor.

        :raises HermeticSessionError: Any part of the session failed to come up.

        :return: The environment the session runs in.
        :rtype: dict(str, str)
        """

        try:
            return self._boot()
        except Exception:
            # __exit__ never runs if __enter__ raises, so clean up here.
            try:
                self.teardown()
            except Exception as cleanup_error:  # noqa: BLE001  pylint: disable=broad-exception-caught
                # The boot failure is the one worth reading, keep it.
                warnings.warn(f"teardown after a failed boot: {cleanup_error}")
            raise

    def _boot(self):
        """
        Do the actual booting, in the one order that works.

        :return: The environment the session runs in.
        :rtype: dict(str, str)
        """

        _check_first_session()
        _check_binaries()

        self._saved_environment = dict(os.environ)
        self.temporary_root = tempfile.mkdtemp(prefix="dogtail-hermetic-")
        for name in ("config", "data", "cache", "state"):
            os.makedirs(os.path.join(self.temporary_root, name), exist_ok=True)

        runtime_directory = os.path.join(self.temporary_root, "runtime")
        os.makedirs(runtime_directory, mode=0o700, exist_ok=True)

        self._boot_bus()
        self._boot_registryd()
        self._boot_mutter(runtime_directory)

        self.environment = {
            **os.environ,
            "XDG_SESSION_TYPE": "wayland",
            "AT_SPI_BUS_ADDRESS": self.bus_address,
            "DBUS_SESSION_BUS_ADDRESS": self.bus_address,
            "WAYLAND_DISPLAY": self.wayland_display,
            "XDG_RUNTIME_DIR": runtime_directory,
            "XDG_CONFIG_HOME": os.path.join(self.temporary_root, "config"),
            "XDG_DATA_HOME": os.path.join(self.temporary_root, "data"),
            "XDG_CACHE_HOME": os.path.join(self.temporary_root, "cache"),
            "XDG_STATE_HOME": os.path.join(self.temporary_root, "state"),
            # A host NO_AT_BRIDGE=1 leaks in and kills the atk bridge silently.
            "NO_AT_BRIDGE": "0",
        }
        os.environ.update(self.environment)

        global _booted_in_this_process  # pylint: disable=global-statement
        _booted_in_this_process = True

        return self.environment

    def _spawn(self, name, command, environment):
        """
        Start a service and send its output to a log file.

        Without the log, a session that will not boot in CI tells you nothing.

        :param name: Short name of the service, used for the log file.
        :type name: str

        :param command: Argument list to execute.
        :type command: list(str)

        :param environment: Environment to start the service in.
        :type environment: dict(str, str)

        :return: The running process.
        :rtype: subprocess.Popen
        """

        log_path = os.path.join(self.temporary_root, f"{name}.log")
        self._logs[name] = log_path
        with open(log_path, "wb") as log:
            return subprocess.Popen(
                command, env=environment, stdout=log, stderr=subprocess.STDOUT,
                preexec_fn=_die_with_parent,  # noqa: PLW1509 - see _die_with_parent
            )

    def _log_tail(self, name, lines=20):
        """
        Read the end of a service log, for error messages.

        :param name: Short name of the service.
        :type name: str

        :param lines: How many lines to return, defaults to 20
        :type lines: int, optional

        :return: The last lines of the log, or a note saying why there are none.
        :rtype: str
        """

        path = self._logs.get(name)
        if not path or not os.path.exists(path):
            return f"(no {name} log)"

        with open(path, "r", errors="replace") as handle:
            tail = handle.read().splitlines()[-lines:]

        return "\n".join(tail) or f"({name} log empty)"

    def _boot_bus(self):
        """
        Start a private session bus and read the address it prints.

        :raises HermeticSessionError: The bus died or never printed an address.
        """

        # Not --fork: a forked daemon is orphaned onto pid 1, and a pid 1 that
        # does not reap leaves it a zombie that os.kill(pid, 0) calls alive.
        self._dbus_process = self._spawn(
            "dbus", ["dbus-daemon", "--session", "--print-address=1"], os.environ,
        )

        deadline = time.time() + self.boot_timeout
        while time.time() < deadline:
            with open(self._logs["dbus"], errors="replace") as handle:
                line = handle.readline()
            if line.endswith("\n"):
                self.bus_address = line.strip()
                return
            if self._dbus_process.poll() is not None:
                raise HermeticSessionError(
                    f"dbus-daemon exited during boot\n"
                    f"--- dbus log ---\n{self._log_tail('dbus')}"
                )
            time.sleep(0.05)

        raise HermeticSessionError(
            f"timed out waiting for the session bus address\n"
            f"--- dbus log ---\n{self._log_tail('dbus')}"
        )

    def _boot_registryd(self):
        """
        Start at-spi2-registryd on the private bus and wait for its name.

        :raises HermeticSessionError: Registryd never claimed its bus name.
        """

        environment = {**os.environ, "AT_SPI_BUS_ADDRESS": self.bus_address,
                       "DBUS_SESSION_BUS_ADDRESS": self.bus_address}
        self._registryd_process = self._spawn("registryd", [_find_registryd()], environment)
        self._wait_for_name(REGISTRY_NAME, environment, "registryd")

    def _wait_for_name(self, name, environment, log_name):
        """
        Block until a D-Bus name has an owner.

        :param name: The bus name to wait for.
        :type name: str

        :param environment: Environment pointing at the private bus.
        :type environment: dict(str, str)

        :param log_name: Service log to quote if the wait times out.
        :type log_name: str

        :raises HermeticSessionError: The name never appeared in time.
        """

        deadline = time.time() + self.boot_timeout
        while time.time() < deadline:
            result = subprocess.run(
                ["dbus-send", "--session", "--dest=org.freedesktop.DBus",
                 "--type=method_call", "--print-reply",
                 "/org/freedesktop/DBus", "org.freedesktop.DBus.NameHasOwner",
                 f"string:{name}"],
                env=environment, capture_output=True, text=True, check=False,
            )
            if "boolean true" in result.stdout:
                return
            time.sleep(0.1)

        raise HermeticSessionError(
            f"timed out waiting for D-Bus name {name}\n"
            f"--- {log_name} log ---\n{self._log_tail(log_name)}"
        )

    def _boot_mutter(self, runtime_directory):
        """
        Start headless mutter with a virtual monitor.

        :param runtime_directory: Directory mutter puts its wayland socket in.
        :type runtime_directory: str

        :raises HermeticSessionError: Mutter died or never came up in time.
        """

        from dogtail.hermetic.mutter import check_mutter_version

        check_mutter_version()

        environment = {
            **os.environ,
            "DBUS_SESSION_BUS_ADDRESS": self.bus_address,
            "XDG_RUNTIME_DIR": runtime_directory,
        }
        self._mutter_process = self._spawn(
            "mutter",
            ["mutter", "--headless", "--no-x11",
             "--virtual-monitor", self.virtual_monitor,
             "--wayland-display", self.wayland_display],
            environment,
        )

        socket_path = os.path.join(runtime_directory, self.wayland_display)
        deadline = time.time() + self.boot_timeout
        while time.time() < deadline:
            if os.path.exists(socket_path):
                break
            if self._mutter_process.poll() is not None:
                raise HermeticSessionError(
                    f"mutter exited during boot\n"
                    f"--- mutter log ---\n{self._log_tail('mutter')}"
                )
            time.sleep(0.1)
        else:
            raise HermeticSessionError(
                f"timed out waiting for mutter's wayland socket\n"
                f"--- mutter log ---\n{self._log_tail('mutter')}"
            )

        # The socket shows up before mutter claims its bus names.
        self._wait_for_name(REMOTE_DESKTOP_NAME, environment, "mutter")

    def launch(self, command, extra_environment=None):
        """
        Start the application under test in this session.

        :param command: Argument list to execute.
        :type command: list(str)

        :param extra_environment: Variables to add on top of the session's own,
            defaults to None
        :type extra_environment: dict(str, str), optional

        :raises HermeticSessionError: The session has not booted yet.

        :return: The running application process.
        :rtype: subprocess.Popen
        """

        if self.environment is None:
            raise HermeticSessionError("launch() before boot(), nothing to launch into")

        environment = {**self.environment, "GDK_BACKEND": "wayland",
                       **(extra_environment or {})}

        return subprocess.Popen(
            command, env=environment,
            preexec_fn=_die_with_parent,  # noqa: PLW1509 - see _die_with_parent
        )

    def wait_for_app(self, name, timeout=None):
        """
        Block until the application shows up on the a11y bus.

        The name is matched case-insensitively, as a substring.

        :param name: Name of the application to wait for.
        :type name: str

        :param timeout: Seconds to wait, defaults to three times the boot timeout
        :type timeout: float, optional

        :raises HermeticSessionError: The application never registered, or
            registered with an empty tree.

        :return: The application node.
        :rtype: dogtail.tree.Node
        """

        import dogtail.tree  # Only safe once boot() has set the environment.

        timeout = 3 * self.boot_timeout if timeout is None else timeout
        needle = name.lower()
        deadline = time.time() + timeout
        application = None
        while time.time() < deadline:
            for child in dogtail.tree.root.children:
                if needle in (child.name or "").lower():
                    application = child
                    break
            # An empty tree is usually a dead atk bridge, but give it the
            # timeout before saying so.
            if application is not None and application.children:
                return application
            time.sleep(0.3)

        if application is not None:
            raise HermeticSessionError(
                f"app {name!r} registered but its tree is empty. that's the atk "
                f"bridge disabled, not a slow app - check NO_AT_BRIDGE isn't set "
                f"to 1 in the app's environment, and that at-spi2-atk is installed"
            )

        seen = [child.name for child in dogtail.tree.root.children]
        raise HermeticSessionError(
            f"app {name!r} never registered on the a11y bus; saw: {seen}"
        )

    def _stop(self, processes):
        """
        Terminate the given processes, then reap them.

        A mutter surviving one test per run is how a CI machine ends up with two
        hundred of them, so do not just trust SIGTERM.

        :param processes: Pairs of name and process, where the process may be None.
        :type processes: tuple(tuple(str, subprocess.Popen))

        :return: Names of the processes still running after a SIGKILL.
        :rtype: list(str)
        """

        processes = [(name, process) for name, process in processes if process is not None]
        leaked = []

        for _, process in processes:
            process.send_signal(signal.SIGTERM)

        for name, process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                warnings.warn(f"{name} ignored SIGTERM, killing it")
                process.kill()
                try:
                    # SIGKILL is asynchronous, so wait or a good teardown
                    # reports a leak that is merely still dying.
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    leaked.append(name)

        return leaked

    def teardown(self):
        """
        Stop every service, remove the temporary directory, restore the environment.

        :raises HermeticSessionError: Something survived a SIGKILL.
        """

        # The bus goes last, the other two want it alive to shut down cleanly.
        leaked = self._stop((("mutter", self._mutter_process),
                             ("registryd", self._registryd_process)))
        leaked += self._stop((("dbus-daemon", self._dbus_process),))

        if self.temporary_root and os.path.isdir(self.temporary_root):
            shutil.rmtree(self.temporary_root, ignore_errors=True)

        if self._saved_environment is not None:
            # A dead bus address left in os.environ poisons the next spawn.
            os.environ.clear()
            os.environ.update(self._saved_environment)
            self._saved_environment = None

        if leaked:
            raise HermeticSessionError(f"survived SIGKILL: {', '.join(leaked)}")

    def monitor_size(self):
        """
        Report the size of the virtual monitor the session booted.

        :return: Width and height in pixels.
        :rtype: tuple(int, int)
        """

        width, _, height = self.virtual_monitor.partition("@")[0].partition("x")

        return int(width), int(height)

    def install_input(self):
        """
        Point dogtail's input at this session, with the coordinate guard armed.

        :return: The installed input backend.
        :rtype: dogtail.hermetic.mutter.MutterInputBackend
        """

        from dogtail.hermetic.mutter import install  # noqa: I001 - gi imports below

        import gi
        gi.require_version("Gdk", "3.0")
        from gi.repository import Gdk  # Keep the Gdk 3.0 pin local.

        if Gdk.Display.get_default() is None:
            # Keysym lookups in rawinput need an open display, and a headless
            # runner never opens one by itself.
            Gdk.Display.open(self.wayland_display)

        return install(bus_address=self.bus_address, monitor_size=self.monitor_size())

    def fullscreen(self, application_node, menu="View", item="Fullscreen"):
        """
        Drive the application's own fullscreen menu item and wait for the frame.

        Fullscreen is the only state where at-spi's window-local coordinates
        equal the screen coordinates injection wants. Anything else and click()
        refuses, see mutter.install. It goes through the application's own menu
        because nothing can fullscreen a window from outside without
        gnome-shell, so applications with no such item do not get coordinate
        clicking at all.

        :param application_node: The application to fullscreen.
        :type application_node: dogtail.tree.Node

        :param menu: Menu holding the fullscreen item, defaults to "View"
        :type menu: str, optional

        :param item: The fullscreen item itself, defaults to "Fullscreen"
        :type item: str, optional

        :raises HermeticSessionError: The window never filled the monitor.

        :return: The now fullscreen frame.
        :rtype: dogtail.tree.Node
        """

        target = self.monitor_size()
        frame = application_node.child(roleName="frame")
        if frame.extents[2:] == target:
            return frame

        application_node.child(menu, roleName="menu").doActionNamed("click")
        do_delay(config.action_delay)
        application_node.child(item).doActionNamed("click")

        deadline = time.time() + self.boot_timeout
        while time.time() < deadline:
            frame = application_node.child(roleName="frame")
            if frame.extents[2:] == target:
                return frame
            time.sleep(0.2)

        raise HermeticSessionError(
            f"{menu} > {item} didn't fullscreen the window: frame is "
            f"{frame.extents[2:]}, monitor is {target}"
        )


def dump_tree(node, max_depth=6, _depth=0, _output=None):
    """
    Dump the AT-SPI tree below a node.

    What you print instead of a screenshot when a test fails.

    :param node: Node to dump.
    :type node: dogtail.tree.Node

    :param max_depth: How deep to walk, defaults to 6
    :type max_depth: int, optional

    :return: The tree, one indented node per line.
    :rtype: str
    """

    output = [] if _output is None else _output

    try:
        output.append("  " * _depth + f"{node.roleName}: {node.name!r}")
    except Exception as error:  # noqa: BLE001  pylint: disable=broad-exception-caught
        output.append("  " * _depth + f"<unreadable node: {error}>")

        return "\n".join(output)

    if _depth < max_depth:
        try:
            for child in node.children:
                dump_tree(child, max_depth, _depth + 1, output)
        except Exception as error:  # noqa: BLE001  pylint: disable=broad-exception-caught
            output.append("  " * (_depth + 1) + f"<unreadable children: {error}>")

    return "\n".join(output)


def demo():
    """
    Check the lifecycle rules that have no other coverage.

    The failed boot goes first, as it does not burn the one-per-process budget.
    The real checks live in tests/.
    """

    failed = HermeticSession(boot_timeout=0.5)
    failed.virtual_monitor = "not-a-resolution"
    try:
        failed.boot()
        raise AssertionError("expected a bad --virtual-monitor to fail the boot")
    except HermeticSessionError as error:
        assert "mutter" in str(error), error
        assert failed._mutter_process.poll() is not None, "mutter left running after failed boot"

    with HermeticSession() as environment:
        assert os.path.exists(
            os.path.join(environment["XDG_RUNTIME_DIR"], environment["WAYLAND_DISPLAY"])
        )
        assert os.environ["AT_SPI_BUS_ADDRESS"] == environment["AT_SPI_BUS_ADDRESS"]

    try:
        HermeticSession().boot()
        raise AssertionError("expected the second session to be refused")
    except HermeticSessionError as error:
        assert "already booted" in str(error), error

    print("HermeticSession demo: OK")


if __name__ == "__main__":
    demo()
