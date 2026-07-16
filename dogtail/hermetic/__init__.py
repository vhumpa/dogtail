"""
Hermetic session support for dogtail: a bare mutter, no gnome-shell, no PipeWire.
"""

from dogtail.hermetic.session import HermeticSession
from dogtail.hermetic.mutter import MutterInputBackend, install as install_mutter_backend

__all__ = ["HermeticSession", "MutterInputBackend", "install_mutter_backend"]
