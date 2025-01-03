import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("autoMOVI")
        self.setGeometry(100, 100, 800, 600)

        self.tray_icon = self.setup_tray_icon()
        self.tray_icon.show()


    def setup_tray_icon(self):
        """Sets up the system tray icon."""
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(QIcon("C:/Users/jdrqu/Documents/autoMOVI/src/ui/automovi.png"))  # use your correct icon path
        tray_icon.setToolTip("autoMOVI")

        menu = QMenu(self)
        show_action = menu.addAction("Show")
        exit_action = menu.addAction("Exit")
        show_action.triggered.connect(self.show_window)
        exit_action.triggered.connect(QApplication.instance().quit)

        tray_icon.setContextMenu(menu)
        tray_icon.activated.connect(self.on_tray_icon_activated)
        return tray_icon


    def show_window(self):
         """Shows the main window, and restores to normal size"""
         self.show()
         current_state = self.windowState()
         self.setWindowState(current_state & ~Qt.WindowState.Minimized)  # unminimize



    def on_tray_icon_activated(self, reason):
        """Handles double-clicks on the tray icon to show or hide the window."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()


    def closeEvent(self, event):
        """Override the closeEvent to hide the window instead of closing it."""
        event.ignore()
        self.hide()
        QMessageBox.information(
            self, "autoMOVI", "autoMOVI is running in the system tray."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())