# Mixin interfaces for writing generalised tests across applications in a category:
class WebBrowser:
    """Mixin/interface for writing cross-browser tests"""
    def browseToLocalFile(self, filename):
        """Test hook to test viewing a local file."""
        raise NotImplementedError

    def browseToUrl(self, urlString):
        """Test hook to test browsing a URL."""
        raise NotImplementedError

class EmailClient:
    """Mixin/interface for writing tests for multiple email clients"""
    def importSingleEmail(self, filename):
        """Test hook to test importing a single email."""
        raise NotImplementedError

class FileBrowser:
    """Mixin/interface for writing tests for multiple file browser applications"""
    def viewFolder(self, directory):
        """Test hook to open a view of the directory."""
        raise NotImplementedError

class ChatClient:
    """Mixin/interface for writing tests for multiple chat clients (xchat, Gaim, Konversation, Kopete)"""

class WordProcessor:
    """Mixin/interface for writing tests for word processor apps (OpenOffice.org Writer, Abiword, KWord)"""

class Spreadsheet:
    """Mixin/interface for writing tests for spreadsheet apps (OpenOffice.org Calc, Gnumeric, KSpread)"""

class PresentationApp:
    """Mixin/interface for writing tests for presentation apps (OpenOffice.org Impress, KPresenter)"""

class DesktopPanel:
    """Mixin/interface for writing tests for multiple implementations of the desktop panel"""
    def applications(self):
        """Get a list of MenuItemRef instances for every user-visible application launchable from the panel"""
        raise NotImplementedError

    def get():
        """Static method to get an instance of the DesktopPanel in use, be it GnomePanel or Kicker"""
        raise NotImplementedError
    get = staticmethod(get)
