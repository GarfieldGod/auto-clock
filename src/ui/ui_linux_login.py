from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialogButtonBox, QFormLayout, QPushButton, QLineEdit, QDialog, QHBoxLayout, QLabel, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt
import os

from src.utils.utils import Utils
from src.ui.ui_message import MessageBox
from src.extend.auto_linux_login import auto_linux_login_off, auto_linux_login_on, check_auto_login_status, validate_linux_credentials, get_linux_credentials_status
from src.extend.auto_linux_sudo import save_sudoers_config, check_sudo_permission, get_sudo_install_commands
from src.utils.const import AppPath, Key


class LinuxLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 Linux 自动登录")
        self.setWindowIcon(QIcon(Utils.get_ico_path()))
        self.name_edit = QLineEdit()
        
        # 在Linux中，密码通常不是必需的，但保留输入框以保持UI一致性
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Linux通常不需要密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        
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
        
        self.button_clear_auto_login = QPushButton("清除")
        self.button_clear_auto_login.clicked.connect(self.clear_auto_login)
        
        # sudo权限配置相关控件
        self.button_config_sudo = QPushButton("配置sudo权限")
        self.button_config_sudo.clicked.connect(self.config_sudo_permission)
        
        # sudo权限状态显示
        self.sudo_status_text = QLabel("正在检查sudo权限...")
        self.sudo_status_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 账号验证状态显示
        self.credentials_status_text = QLabel("请输入账号信息")
        self.credentials_status_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.credentials_status_text.setStyleSheet("color: orange;")
        
        # 安装命令显示区域
        self.install_commands_text = QTextEdit()
        self.install_commands_text.setMaximumHeight(100)
        self.install_commands_text.setReadOnly(True)
        self.install_commands_text.setPlaceholderText("sudo权限配置命令将在这里显示...")
        
        # 创建状态文本显示（图标直接嵌入文本中）
        self.status_text = QLabel("正在检查状态...")
        # 左对齐显示
        self.status_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 主表单布局
        form = QFormLayout()
        form.addRow("Linux 用户名:", self.name_edit)
        form.addRow("密码 (可选):", password_layout)
        form.addRow("账号状态:", self.credentials_status_text)
        form.addRow("清除自动登录:", self.button_clear_auto_login)
        
        # 添加分隔线
        separator_label = QLabel("─" * 30)
        separator_label.setAlignment(Qt.AlignCenter)
        separator_label.setStyleSheet("color: gray; margin: 10px 0;")
        form.addRow(separator_label)
        
        # sudo权限配置区域
        form.addRow("sudo权限状态:", self.sudo_status_text)
        form.addRow("配置sudo权限:", self.button_config_sudo)
        form.addRow("安装命令:", self.install_commands_text)
        
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
        
        # 添加提示信息
        self.warning_label = QLabel("⚠️ 注意：此操作需要管理员权限，请确保应用以sudo或管理员身份运行\n💡 sudo权限用于关机、睡眠等系统操作，创建定时任务前需要配置")
        self.warning_label.setStyleSheet("color: orange;")
        self.warning_label.setWordWrap(True)
        form.addRow(self.warning_label)
        
        # 初始检查并更新状态显示
        self.update_status_display()
        self.update_sudo_status_display()
        
        # 加载已保存的账号信息
        self.load_credentials()
        
        # 连接输入框变化事件进行实时验证
        self.name_edit.textChanged.connect(self.validate_credentials)
        self.password_edit.textChanged.connect(self.validate_credentials)

    def values(self):
        return self.name_edit.text().strip(), self.password_edit.text().strip()

    def on_accept(self):
        try:
            username, password = self.values()
            if username:
                # 保存用户名信息
                self.save_credentials()
                
                # 调用auto_linux_login_on，不显示重复的弹窗
                backup_path = auto_linux_login_on(username, password if password else None)
                # 更新状态显示
                self.update_status_display()
                self.accept()
                MessageBox("设置成功！重启系统后生效。\n备份文件已保存。")
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
            backup_path = auto_linux_login_off()
            # 更新状态显示
            self.update_status_display()
            MessageBox(f"清除成功！\n清除前的备份文件：{backup_path}\n重启系统后生效。")
        except Exception as e:
            # 即使出错也尝试更新状态显示
            self.update_status_display()
            MessageBox(f"清除失败！\n错误：{e}")

    def config_sudo_permission(self):
        """配置sudo权限"""
        try:
            username = self.name_edit.text().strip() or None
            
            # 生成sudoers配置文件
            config_path = save_sudoers_config(username)
            
            # 获取安装命令
            install_commands = get_sudo_install_commands(config_path)
            
            # 显示安装命令
            commands_text = "\n".join(install_commands)
            self.install_commands_text.setPlainText(commands_text)
            
            # 更新sudo权限状态
            self.update_sudo_status_display()
            
            MessageBox(f"sudoers配置文件已生成！\n文件路径：{config_path}\n\n请在终端中执行以下命令完成安装：\n{commands_text}\
                \n\n显示类似如下字样则为配置成功:\
                \n/etc/sudoers: parsed OK\n/etc/sudoers.d/README: parsed OK\n/etc/sudoers.d/auto-clock: parsed OK")
            
        except Exception as e:
            MessageBox(f"配置sudo权限失败！\n错误：{str(e)}")

    def update_sudo_status_display(self):
        """更新sudo权限状态显示"""
        has_permission, status_text = check_sudo_permission()
        
        if has_permission is True:
            # sudo权限已配置 - 使用绿色勾选图标
            self.sudo_status_text.setText("✅已配置")
            self.sudo_status_text.setStyleSheet("color: green;")
        elif has_permission is False:
            # sudo权限未配置 - 使用红色叉号图标
            self.sudo_status_text.setText("❌未配置")
            self.sudo_status_text.setStyleSheet("color: red;")
        else:
            # 无法检查状态 - 使用黄色问号图标
            self.sudo_status_text.setText("❓检查失败")
            self.sudo_status_text.setStyleSheet("color: orange;")

    def validate_credentials(self):
        """实时验证账号信息"""
        username = self.name_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username:
            self.credentials_status_text.setText("请输入用户名")
            self.credentials_status_text.setStyleSheet("color: orange;")
            return
        
        try:
            is_valid, status_msg = validate_linux_credentials(username, password if password else None)
            
            if is_valid is True:
                # 验证成功 - 使用绿色勾选图标
                self.credentials_status_text.setText("✅有效")
                self.credentials_status_text.setStyleSheet("color: green;")
            elif is_valid is False:
                # 验证失败 - 使用红色感叹号图标
                self.credentials_status_text.setText("⚠️无效")
                self.credentials_status_text.setStyleSheet("color: red;")
                # 设置工具提示显示详细信息
                self.credentials_status_text.setToolTip(status_msg)
            else:
                # 无法验证 - 使用黄色问号图标
                self.credentials_status_text.setText("❓未知")
                self.credentials_status_text.setStyleSheet("color: orange;")
                self.credentials_status_text.setToolTip(status_msg)
                
        except Exception as e:
            # 验证出错 - 使用红色感叹号图标
            self.credentials_status_text.setText("⚠️验证失败")
            self.credentials_status_text.setStyleSheet("color: red;")
            self.credentials_status_text.setToolTip(f"验证出错：{str(e)}")

    def get_credentials_status(self):
        """获取当前账号验证状态，供任务创建时使用"""
        username = self.name_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username:
            return False, "未配置用户名"
        
        try:
            is_valid, status_msg = validate_linux_credentials(username, password if password else None)
            return is_valid, status_msg
        except Exception as e:
            return False, f"验证失败：{str(e)}"

    def load_credentials(self):
        """加载已保存的Linux账号信息"""
        try:
            if os.path.exists(AppPath.DataJson):
                data = Utils.read_dict_from_json(AppPath.DataJson)
                if data:
                    self.name_edit.setText(data.get("LinuxUserName", ""))
                    # 出于安全考虑，不自动加载密码，但可以加载用户名
                    self.validate_credentials()
        except Exception as e:
            from src.utils.log import Log
            Log.warning(f"加载Linux账号信息失败: {str(e)}")

    def save_credentials(self):
        """保存Linux账号信息（只保存用户名，不保存密码）"""
        try:
            username = self.name_edit.text().strip()
            if username:
                # 读取现有数据
                data = {}
                if os.path.exists(AppPath.DataJson):
                    data = Utils.read_dict_from_json(AppPath.DataJson) or {}
                
                # 更新Linux用户名
                data["LinuxUserName"] = username
                
                # 保存数据
                Utils.write_dict_to_file(AppPath.DataJson, data)
                from src.utils.log import Log
                Log.info("Linux账号信息已保存")
        except Exception as e:
            from src.utils.log import Log
            Log.warning(f"保存Linux账号信息失败: {str(e)}")
