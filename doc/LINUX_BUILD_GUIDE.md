# Auto-Clock Linux 打包指南

本指南介绍如何在Linux系统上打包Auto-Clock应用程序。

## 前置要求

### 1. 系统要求
- Linux系统（Ubuntu 20.04+、Debian 10+、CentOS 8+等）
- Python 3.8+
- 至少2GB可用磁盘空间

### 2. 安装依赖

#### Ubuntu/Debian系统
```bash
# 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0 libxcb1-dev libx11-dev \
    libxkbcommon-x11-0 libegl1-mesa-dev libgl1-mesa-glx libfontconfig1-dev \
    libicu-dev libsqlite3-dev libxss1 libgconf-2-4 libxtst6 libasound2-dev libpulse-dev
```

#### CentOS/RHEL/Fedora系统
```bash
# 安装系统依赖
sudo yum install -y python3 python3-pip
sudo yum install -y libX11-devel libXext-devel libXtst-devel libxcb-devel \
    mesa-libGL-devel libxkbcommon-devel libXcursor-devel libXi-devel
```

### 3. 安装Python依赖
```bash
# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt

# 安装PyInstaller
pip install pyinstaller
```

## 打包方法

### 方法1：使用打包脚本（推荐）

1. 给脚本添加执行权限：
```bash
chmod +x linux_build.sh
```

2. 运行打包脚本：
```bash
./linux_build.sh
```

3. 打包完成后，可执行文件位于 `dist/auto_clock`

### 方法2：手动打包

```bash
# 清理之前的构建
rm -rf build dist

# 使用PyInstaller打包
pyinstaller pack_linux.spec

# 或者使用单文件模式
pyinstaller --onefile --name auto_clock entry.py
```

## 打包后的文件结构

```
dist/
└── auto_clock          # 可执行文件
```

## 使用打包后的应用

### 1. 准备配置文件

首次运行前，需要准备以下文件：
- `config.json` - 配置文件（可以从源码目录复制）
- `drivers/linux/msedgedriver` - Edge浏览器驱动

```bash
# 复制配置文件到可执行文件同目录
cp config.json dist/
cp -r drivers dist/

# 确保驱动有执行权限
chmod +x dist/drivers/linux/msedgedriver
```

### 2. 运行应用

#### 图形界面模式
```bash
./dist/auto_clock
```

#### 无头模式执行任务
```bash
./dist/auto_clock --headless --task_id=YOUR_TASK_ID
```

#### 任务模式
```bash
./dist/auto_clock --task_id=YOUR_TASK_ID
```

### 3. 查看帮助
```bash
./dist/auto_clock --help
```

## 常见问题

### 1. 打包失败

**问题**: PyInstaller未找到
```bash
pip install pyinstaller
```

**问题**: 缺少系统依赖
```bash
# 参考上面的"安装依赖"部分
```

### 2. 运行时错误

**问题**: Qt平台插件错误
```bash
# 安装Qt相关依赖
sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0
```

**问题**: 权限不足
```bash
# 某些操作需要sudo权限
sudo ./dist/auto_clock --task_id=YOUR_TASK_ID
```

### 3. 文件大小优化

如果打包后的文件太大，可以：

1. 使用UPX压缩（已在spec文件中启用）：
```bash
sudo apt-get install upx
```

2. 排除不必要的模块：
编辑 `pack_linux.spec`，在 `excludes` 中添加不需要的模块

## 分发应用

### 创建安装包

```bash
# 创建tar.gz压缩包
cd dist
tar -czf auto_clock_linux_x64.tar.gz auto_clock config.json drivers/

# 创建安装脚本
cat > install.sh << 'EOF'
#!/bin/bash
echo "安装 Auto-Clock..."
mkdir -p ~/.local/bin
cp auto_clock ~/.local/bin/
chmod +x ~/.local/bin/auto_clock
echo "安装完成！"
echo "运行: auto_clock"
EOF
chmod +x install.sh
```

### 系统要求说明

在分发时，请告知用户需要安装以下依赖：

**Ubuntu/Debian**:
```bash
sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0 libx11-6
```

**CentOS/RHEL**:
```bash
sudo yum install -y libX11 libXext libXtst
```

## 注意事项

1. **驱动文件**: 确保Edge驱动与目标系统的Edge浏览器版本匹配
2. **权限**: 网络控制等功能可能需要sudo权限
3. **配置文件**: 打包后的应用会在 `~/.local/share/auto-clock/` 目录存储数据
4. **日志文件**: 日志保存在 `~/.local/share/auto-clock/log/` 目录

## 进阶配置

### 创建桌面快捷方式

```bash
cat > ~/.local/share/applications/auto-clock.desktop << EOF
[Desktop Entry]
Name=Auto Clock
Comment=自动打卡工具
Exec=/path/to/auto_clock
Icon=/path/to/icon.png
Terminal=false
Type=Application
Categories=Utility;
EOF
```

### 设置开机自启动

```bash
# 创建systemd服务
sudo cat > /etc/systemd/system/auto-clock.service << EOF
[Unit]
Description=Auto Clock Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/path/to/auto_clock --headless
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl enable auto-clock.service
sudo systemctl start auto-clock.service
```

## 技术支持

如有问题，请查看：
- [LINUX_INSTALL_GUIDE.md](LINUX_INSTALL_GUIDE.md) - 运行时问题
- [README.md](README.md) - 使用说明
- GitHub Issues - 提交bug报告
