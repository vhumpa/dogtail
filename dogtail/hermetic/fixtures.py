"""
Pytest fixtures for hermetic sessions. Import them into your conftest.py:

    from dogtail.hermetic.fixtures import hermetic_session  # noqa: F401

They are kept out of dogtail/hermetic/__init__.py on purpose, so that importing
the package never needs pytest installed.
"""

import pytest

from dogtail.hermetic.session import HermeticSession


@pytest.fixture(scope="session")
def hermetic_session():
    """
    Boot one HermeticSession for the whole run.

    The scope is session rather than module because pytest runs every test
    module in one process, and libatspi caches its desktop connection in C on
    first use, so a second boot would silently hand back the first one's dead
    bus. Anything narrower than session scope gives the second module a dead
    session.

    :return: The booted session.
    :rtype: dogtail.hermetic.session.HermeticSession
    """

    session = HermeticSession()
    session.boot()
    try:
        yield session
    finally:
        session.teardown()
