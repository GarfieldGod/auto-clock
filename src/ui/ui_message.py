from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QDialogButtonBox, QHBoxLayout, QVBoxLayout, QLabel, QDialog

from src.utils.utils import Utils


class MessageBox(QDialog):
    def __init__(self, message, message_name="Message", parent=None, need_check=False, message_only=True):
        super().__init__(parent)
        self.setWindowTitle(message_name)
        self.setWindowIcon(QIcon(Utils.get_ico_path()))

        label = QLabel(str(message))
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        label.setFont(font)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        layout_center_label = QHBoxLayout()
        layout_center_label.addStretch(1)
        layout_center_label.addWidget(label)
        layout_center_label.addStretch(1)

        if need_check:
            button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button.rejected.connect(self.reject)
        else:
            button = QDialogButtonBox(QDialogButtonBox.Ok)
        button.accepted.connect(self.accept)
        layout_center_button = QHBoxLayout()
        layout_center_button.addStretch(1)
        layout_center_button.addWidget(button)
        layout_center_button.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addLayout(layout_center_label)
        layout.addStretch()
        layout.addLayout(layout_center_button)
        if message_only:
            self.exec_()