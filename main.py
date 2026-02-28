import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QLabel,
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
import os
from info import InfoTab
from update import UpdateTab
from test import TestTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Factory Test Tool")
        self.resize(600, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # create three pages
        self.tab_info = InfoTab()
        self.tab_upgrade = UpdateTab()
        self.tab_test = TestTab()

        self.tabs.addTab(self.tab_info, "Info")
        self.tabs.addTab(self.tab_upgrade, "Update")
        self.tabs.addTab(self.tab_test, "TEST")

    def center_window(self):
        """Center the main window on the primary screen."""
        screen = QGuiApplication.primaryScreen()
        if not screen:
            return

        # Use frame geometry so borders/titlebar are accounted for
        qr = self.frameGeometry()
        cp = screen.availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showEvent(self, event):
        """Ensure the window is centered after it is shown."""
        super().showEvent(event)
        # Defer centering until after the window is fully shown/layouted
        QTimer.singleShot(0, self.center_window)

    # =========================
    # Tab 3 : TEST
    # =========================
    def create_test_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("TEST"))
        widget.setLayout(layout)
        return widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
