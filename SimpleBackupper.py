import sys
import os
import shutil
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar, QComboBox, QMenuBar, QMenu, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

class SimpleBackupper(QWidget):
    CONFIG_FILE = "backup_config.json"
    LANG_DIR = "lang"

    def __init__(self):
        super().__init__()
        self.loadConfig()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SimpleBackupper")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowIcon(QIcon('ico.png'))

        layout = QVBoxLayout()

        # Menu for language selection
        self.menu_bar = QMenuBar()

        self.language_menu = QMenu(self)
        self.french_action = QAction(self)
        self.french_action.triggered.connect(lambda: self.set_language("fr"))
        self.english_action = QAction(self)
        self.english_action.triggered.connect(lambda: self.set_language("en"))
        self.language_menu.addAction(self.french_action)
        self.language_menu.addAction(self.english_action)
        self.menu_bar.addMenu(self.language_menu)

        layout.setMenuBar(self.menu_bar)

        # UI elements for backup functionality
        self.source_label = QLabel(self)
        self.source_lineedit = QLineEdit(self.config.get("source_dir", "C:\\Users"))
        self.source_lineedit.textChanged.connect(self.saveConfig)
        self.source_button = QPushButton(self)
        self.source_button.clicked.connect(self.selectSourceDirectory)

        self.destination_label = QLabel(self)
        self.destination_lineedit = QLineEdit(self.config.get("dest_dir", ""))
        self.destination_lineedit.textChanged.connect(self.saveConfig)
        self.destination_button = QPushButton(self)
        self.destination_button.clicked.connect(self.selectDestinationPath)

        self.interval_label = QLabel(self)
        self.interval_combobox = QComboBox(self)
        self.interval_combobox.addItems(["Continuous", "Daily", "Weekly"])
        self.interval_combobox.currentIndexChanged.connect(self.saveConfig)

        self.backup_button = QPushButton(self)
        self.backup_button.clicked.connect(self.performBackup)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

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

        self.setLayout(layout)

        self.backup_timer = QTimer(self)
        self.backup_timer.timeout.connect(self.performBackup)

        # Load default language or saved one
        self.set_language(self.config.get("language", "en"))

    def loadConfig(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as file:
                self.config = json.load(file)
        else:
            self.config = {}

    def saveConfig(self):
        with open(self.CONFIG_FILE, 'w') as file:
            self.config["source_dir"] = self.source_lineedit.text()
            self.config["dest_dir"] = self.destination_lineedit.text()
            self.config["interval"] = self.interval_combobox.currentText()
            json.dump(self.config, file)

    def set_language(self, lang):
        """Update UI text based on language."""
        self.config["language"] = lang
        self.saveConfig()

        # Load translations from the file with explicit encoding
        with open(os.path.join(self.LANG_DIR, f"{lang}.json"), 'r', encoding='utf-8') as f:
            translations = json.load(f)

        tr = translations[lang]

        self.source_label.setText(tr["source"])
        self.source_button.setText(tr["browse"])
        self.destination_label.setText(tr["destination"])
        self.destination_button.setText(tr["browse"])
        self.interval_label.setText(tr["interval"])
        self.interval_combobox.setItemText(0, tr["continuous"])
        self.interval_combobox.setItemText(1, tr["daily"])
        self.interval_combobox.setItemText(2, tr["weekly"])
        self.backup_button.setText(tr["backup"])

        self.language_menu.setTitle(tr["language"])
        self.french_action.setText(tr["french"])
        self.english_action.setText(tr["english"])

    def selectSourceDirectory(self):
        source_dir = QFileDialog.getExistingDirectory(self, "Select Source Directory", self.source_lineedit.text())
        if source_dir:
            self.source_lineedit.setText(source_dir)

    def selectDestinationPath(self):
        dest_dir = QFileDialog.getExistingDirectory(self, "Select Destination Path", self.destination_lineedit.text())
        if dest_dir:
            self.destination_lineedit.setText(dest_dir)

    def performBackup(self):
        # Backup logic (Copying directory as an example)
        source = self.source_lineedit.text()
        destination = os.path.join(self.destination_lineedit.text(), os.path.basename(source))
        
        try:
            shutil.copytree(source, destination)
            QMessageBox.information(self, "Backup", "Backup completed successfully!")
            self.progress_bar.setValue(100)
            QTimer.singleShot(10000, lambda: self.progress_bar.setValue(0))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup failed: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleBackupper()
    window.show()
    sys.exit(app.exec_())
