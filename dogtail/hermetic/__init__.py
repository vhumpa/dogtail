"""
Hermetic session support for dogtail: a bare mutter, no gnome-shell, no PipeWire.
"""

from dogtail.hermetic.mutter import MutterInputBackend
from dogtail.hermetic.mutter import install as install_mutter_backend
from dogtail.hermetic.session import HermeticSession

__all__ = ["HermeticSession", "MutterInputBackend", "install_mutter_backend"]
