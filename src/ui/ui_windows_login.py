from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialogButtonBox, QFormLayout, QPushButton, QLineEdit, QDialog

from src.utils.utils import Utils
from src.ui.ui_message import MessageBox
from src.extend.auto_windows_login import auto_windows_login_off


class WindowsLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Windows Auto Login")
        self.setWindowIcon(QIcon(Utils.get_ico_path()))
        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.button_clear_auto_login = QPushButton("Clear")
        self.button_clear_auto_login.clicked.connect(self.clear_auto_login)

        form = QFormLayout(self)
        form.addRow("Windows User Name:", self.name_edit)
        form.addRow("Windows User Password:", self.password_edit)
        form.addRow("Clear Auto Login:", self.button_clear_auto_login)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self):
        return self.name_edit.text().strip(), self.password_edit.text().strip()

    def clear_auto_login(self):
        try:
            backup_path = auto_windows_login_off()
            MessageBox(f"Clear Success!\nbackup before clear: {backup_path}")
        except Exception as e:
            MessageBox(f"Clear Failed!\nError: {e}")