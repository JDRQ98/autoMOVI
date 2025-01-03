import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QCalendarWidget, QVBoxLayout, QWidget, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QLabel, QPushButton, QSystemTrayIcon, QMenu, QHBoxLayout
)
from PyQt6.QtGui import QTextCharFormat, QColor, QIcon
from PyQt6.QtCore import Qt, QDate

class CalendarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("autoMOVI Calendar")
        self.setGeometry(100, 100, 600, 400)

        # Load MOVI data from JSON
        self.movi_data = self.load_movi_data()

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Add "Go to Current Date" button
        self.go_to_today_button = QPushButton("Go to Current Date")
        self.go_to_today_button.clicked.connect(self.go_to_today)
        self.layout.addWidget(self.go_to_today_button)

        # Calendar widget
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.on_date_clicked)
        self.layout.addWidget(self.calendar)

        # Add "Update MOVI Status" button
        self.update_status_button = QPushButton("Update MOVI Status")
        self.update_status_button.clicked.connect(self.update_movi_status)
        self.layout.addWidget(self.update_status_button)

        # Update calendar colors
        self.update_calendar_colors()

    def load_movi_data(self):
        """Load MOVI data from JSON file."""
        try:
            with open("movis.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_movi_data(self):
        """Save MOVI data to JSON file."""
        with open("movis.json", "w") as file:
            json.dump(self.movi_data, file, indent=4)

    def update_calendar_colors(self):
        """Update the calendar colors based on MOVI status."""
        format_map = {
            "no_movi": QColor("lightgrey"),
            "pending": QColor("yellow"),
            "in_queue": QColor("blue"),
            "accepted": QColor("green"),
            "rejected": QColor("red"),
        }

        for date_str, status in self.movi_data.items():
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if not date.isValid():
                continue

            char_format = QTextCharFormat()
            char_format.setBackground(format_map.get(status, QColor("lightgrey")))
            self.calendar.setDateTextFormat(date, char_format)

    def on_date_clicked(self, date):
        """Handle clicks on the calendar."""
        date_str = date.toString("yyyy-MM-dd")
        status = self.movi_data.get(date_str, "no_movi")

        if status == "no_movi":
            self.add_new_movi(date_str)
        else:
            self.show_movi_details(date_str, status)

    def add_new_movi(self, date_str):
        """Open a dialog to add a new MOVI."""
        dialog = MOVIDialog(date_str, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.movi_data[date_str] = "in_queue"
            self.save_movi_data()
            self.update_calendar_colors()

    def show_movi_details(self, date_str, status):
        """Show details of the MOVI for the selected date."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"MOVI Details - {date_str}")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Status: {status.capitalize()}"))

        remove_button = QPushButton("Remove MOVI")
        remove_button.clicked.connect(lambda: self.remove_movi(date_str, dialog))
        layout.addWidget(remove_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()

    def remove_movi(self, date_str, dialog):
        """Remove a MOVI from the queue."""
        if date_str in self.movi_data:
            del self.movi_data[date_str]
            self.save_movi_data()
            self.update_calendar_colors()
            dialog.accept()

    def go_to_today(self):
        """Go to the current date on the calendar."""
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.calendar.showSelectedDate()

    def update_movi_status(self):
        """Placeholder for updating MOVI status."""
        # This function will be integrated with the MOVI Status Updater in the future
        print("Update MOVI Status button clicked!")

class MOVIDialog(QDialog):
    def __init__(self, date_str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add MOVI - {date_str}")

        self.layout = QFormLayout(self)
        self.date_label = QLabel(date_str)

        self.layout.addRow("Date:", self.date_label)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("autoMOVI")
        self.setGeometry(100, 100, 600, 400)

        self.tray_icon = self.setup_tray_icon()
        self.tray_icon.show()

        self.calendar_window = CalendarWindow()
        self.setCentralWidget(self.calendar_window)

    def setup_tray_icon(self):
        """Sets up the system tray icon."""
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(QIcon("src/ui/automovi.png"))  # use your correct icon path
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
        """Shows the main window, and restores to normal size."""
        self.show()
        current_state = self.windowState()
        self.setWindowState(current_state & ~Qt.WindowState.WindowMinimized)  # unminimize

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
