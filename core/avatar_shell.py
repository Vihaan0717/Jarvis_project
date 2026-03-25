import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from core.logger import get_logger

logger = get_logger("AvatarShell")

class AvatarShell(QMainWindow):
    def __init__(self, url="http://127.0.0.1:8766/avatar/index.html"):
        super().__init__()
        self.setWindowTitle("JARVIS - Digital Human Interface")
        self.setMinimumSize(1024, 768)
        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setStyleSheet("background-color: #050505;")
        self.browser.setUrl(QUrl(url))

def launch_shell(url="http://127.0.0.1:8766/avatar/index.html"):
    app = QApplication.instance() or QApplication(sys.argv)
    window = AvatarShell(url)
    window.show()
    return app, window
