from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialogButtonBox, QFormLayout, QPushButton, QLineEdit, QDialog, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

from src.utils.utils import Utils
from src.ui.ui_message import MessageBox
from src.extend.auto_windows_login import auto_windows_login_off, auto_windows_login_on, check_auto_login_status


class WindowsLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Windows Auto Login")
        self.setWindowIcon(QIcon(Utils.get_ico_path()))
        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)  # 设置密码框隐藏输入
        
        # 创建密码可见性切换按钮
        self.show_password_btn = QPushButton()
        self.show_password_btn.setFixedSize(24, 24)
        self.show_password_btn.setStyleSheet("border: none; background-color: transparent;")
        
        # 使用锁图标作为默认状态（密码隐藏）
        self.show_password_btn.setText("🔒")
        self.show_password_btn.setToolTip("显示密码")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        
        # 创建水平布局来容纳密码输入框和眼睛图标按钮
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_edit)
        password_layout.addWidget(self.show_password_btn)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        self.button_clear_auto_login = QPushButton("Clear")
        self.button_clear_auto_login.clicked.connect(self.clear_auto_login)
        
        # 创建状态文本显示（图标直接嵌入文本中）
        self.status_text = QLabel("正在检查状态...")
        # 左对齐显示
        self.status_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 主表单布局
        form = QFormLayout()
        form.addRow("Windows User Name:", self.name_edit)
        form.addRow("Windows User Password:", password_layout)
        form.addRow("Clear Auto Login:", self.button_clear_auto_login)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        
        # 创建按钮和状态显示的水平布局
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.status_text)  # 状态文本放在左侧
        bottom_layout.addStretch()  # 拉伸项使按钮靠右
        bottom_layout.addWidget(buttons)  # 按钮放在右侧
        
        form.addRow(bottom_layout)
        
        # 创建主垂直布局，只包含表单
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 初始检查并更新状态显示
        self.update_status_display()

    def values(self):
        return self.name_edit.text().strip(), self.password_edit.text().strip()

    def on_accept(self):
        try:
            username, password = self.values()
            if username:
                # 调用auto_windows_login_on，不显示重复的弹窗
                backup_path = auto_windows_login_on(username, password)
                # 更新状态显示
                self.update_status_display()
                self.accept()
            else:
                MessageBox("用户名不能为空！")
        except Exception as e:
            # 即使出错也尝试更新状态显示
            self.update_status_display()
            MessageBox(f"设置失败！\n错误：{str(e)}")
            
    def toggle_password_visibility(self):
        """切换密码可见性"""
        if self.password_edit.echoMode() == QLineEdit.Password:
            # 显示密码 - 使用普通眼睛图标
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("👁")
            self.show_password_btn.setToolTip("隐藏密码")
        else:
            # 隐藏密码 - 使用闭眼睛+斜杠图标
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("🔒")
            self.show_password_btn.setToolTip("显示密码")
            
    def update_status_display(self):
        """更新自动登录状态显示"""
        enabled, status_text = check_auto_login_status()
        
        if enabled is True:
            # 自动登录已启用 - 使用绿色勾选图标
            self.status_text.setText("✅已启用")
            self.status_text.setStyleSheet("color: green;")
        elif enabled is False:
            # 自动登录未启用 - 使用红色叉号图标
            self.status_text.setText("❌未启用")
            self.status_text.setStyleSheet("color: red;")
        else:
            # 无法检查状态 - 使用黄色问号图标
            self.status_text.setText("❓未知")
            self.status_text.setStyleSheet("color: orange;")

    def clear_auto_login(self):
        try:
            backup_path = auto_windows_login_off()
            # 更新状态显示
            self.update_status_display()
            MessageBox(f"Clear Success!\nbackup before clear: {backup_path}")
        except Exception as e:
            # 即使出错也尝试更新状态显示
            self.update_status_display()
            MessageBox(f"Clear Failed!\nError: {e}")