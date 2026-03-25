import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from core.logger import get_logger

logger = get_logger("AvatarShell")

class AvatarShell(QMainWindow):
    """
    JARVIS Dedicated Desktop Shell.
    Replaces standard browsers (Chrome/Edge) with a custom PyQt6 WebEngine window.
    Bypasses autoplay policies and allows for advanced UI integration.
    """
    def __init__(self, url="http://127.0.0.1:8766/avatar/index.html"):
        super().__init__()
        self.setWindowTitle("JARVIS - Digital Human Interface")
        self.setMinimumSize(1024, 768)
        
        # 1. Setup WebEngine with Autoplay Bypass
        self.browser = QWebEngineView()
        
        # Enable Autoplay without user gesture
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        
        # This is the key for bypassing autoplay policy in QtWebEngine
        self.browser.settings().setAttribute(
            QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False
        )
        self.browser.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self.browser.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        
        # 2. Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # 3. Premium Shell Features
        self.setStyleSheet("background-color: #050505;")
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint) # Uncomment for HUD feel
        # self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        # 4. Load URL
        logger.info(f"Loading Avatar Interface: {url}")
        self.browser.setUrl(QUrl(url))

def launch_shell(url="http://127.0.0.1:8766/avatar/index.html"):
    """Entry point for the shell."""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    window = AvatarShell(url)
    window.show()
    return app, window

if __name__ == "__main__":
    app, window = launch_shell()
    sys.exit(app.exec())
