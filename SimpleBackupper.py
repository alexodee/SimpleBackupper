import sys
import os
import json
import subprocess
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar, QComboBox, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

class SimpleBackupper(QWidget):
    SETTINGS_FILE = "settings.json"

    def __init__(self):
        super().__init__()
        self.loadSettings()
        self.initUI()
        self.setupBackupScheduler()
        self.tray_icon = QSystemTrayIcon(QIcon("ico.png"), self)
        self.setupTrayIcon()
        self.setWindowIcon(QIcon("ico.png"))

    def initUI(self):
        self.setWindowTitle("SimpleBackupper")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.source_label = QLabel("Source Directory", self)
        self.source_lineedit = QLineEdit(self.settings.get("source_dir", ""), self)
        self.source_lineedit.textChanged.connect(self.saveSettings)
        self.source_button = QPushButton("Browse", self)
        self.source_button.clicked.connect(self.selectSourceDirectory)
        self.destination_label = QLabel("Destination Directory", self)
        self.destination_lineedit = QLineEdit(self.settings.get("dest_dir", ""), self)
        self.destination_lineedit.textChanged.connect(self.saveSettings)
        self.destination_button = QPushButton("Browse", self)
        self.destination_button.clicked.connect(self.selectDestinationDirectory)
        self.interval_label = QLabel("Backup Interval", self)
        self.interval_combobox = QComboBox(self)
        self.interval_combobox.addItems(["None", "Continuous (10 minutes)", "Daily", "Weekly", "Monthly"])
        self.interval_combobox.setCurrentText(self.settings.get("interval", "None"))
        self.interval_combobox.currentIndexChanged.connect(self.updateBackupInterval)
        self.backup_button = QPushButton("Backup Now", self)
        self.backup_button.clicked.connect(lambda: self.performBackup(manual=True))
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.last_backup_label = QLabel("Last backup: " + self.settings.get("last_backup", "N/A"))
        self.next_backup_label = QLabel("Next backup: Calculating...")

        layout.addWidget(self.source_label)
        layout.addWidget(self.source_lineedit)
        layout.addWidget(self.source_button)
        layout.addWidget(self.destination_label)
        layout.addWidget(self.destination_lineedit)
        layout.addWidget(self.destination_button)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_combobox)
        layout.addWidget(self.backup_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.last_backup_label)
        layout.addWidget(self.next_backup_label)
        self.setLayout(layout)

    def loadSettings(self):
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, 'r') as file:
                self.settings = json.load(file)
        else:
            self.settings = {}

    def saveSettings(self):
        with open(self.SETTINGS_FILE, 'w') as file:
            self.settings["source_dir"] = self.source_lineedit.text()
            self.settings["dest_dir"] = self.destination_lineedit.text()
            self.settings["interval"] = self.interval_combobox.currentText()
            json.dump(self.settings, file)

    def selectSourceDirectory(self):
        source_dir = QFileDialog.getExistingDirectory(self, "Select Source Directory", self.source_lineedit.text())
        if source_dir:
            self.source_lineedit.setText(source_dir)

    def selectDestinationDirectory(self):
        dest_dir = QFileDialog.getExistingDirectory(self, "Select Destination Directory", self.destination_lineedit.text())
        if dest_dir:
            self.destination_lineedit.setText(dest_dir)

    def updateBackupInterval(self):
        interval_mappings = {
            "None": None,
            "Continuous (10 minutes)": 600000,
            "Daily": 86400000,
            "Weekly": 604800000,
            "Monthly": 2592000000
        }
        interval = self.interval_combobox.currentText()
        if interval != "None":
            self.backup_timer.setInterval(interval_mappings[interval])
            self.backup_timer.start()
            next_backup = datetime.datetime.now() + datetime.timedelta(milliseconds=interval_mappings[interval])
            self.next_backup_label.setText("Next backup: " + next_backup.strftime("%d-%m-%Y %H:%M:%S"))
        else:
            self.backup_timer.stop()
            self.next_backup_label.setText("No scheduled backups")
        self.saveSettings()

    def performBackup(self, manual=False):
        source = self.source_lineedit.text()
        destination = self.destination_lineedit.text()
        cmd = ["robocopy", source, destination, "/MIR"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print(out.decode("utf-8", errors='replace'))
        self.progress_bar.setValue(100)
        self.settings["last_backup"] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.last_backup_label.setText("Last backup: " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        if manual:
            QMessageBox.information(self, "Backup Completed", "Backup was successful!")
        next_interval = self.backup_timer.interval()
        if next_interval:
            next_backup = datetime.datetime.now() + datetime.timedelta(milliseconds=next_interval)
            self.next_backup_label.setText("Next backup: " + next_backup.strftime("%d-%m-%Y %H:%M:%S"))
        self.saveSettings()

    def setupBackupScheduler(self):
        self.backup_timer = QTimer(self)
        self.backup_timer.timeout.connect(self.performBackup)
        self.updateBackupInterval()

    def setupTrayIcon(self):
        menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleBackupper()
    window.show()
    sys.exit(app.exec_())
