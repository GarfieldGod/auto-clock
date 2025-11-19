# Auto-Clock Linux 安装指南

## 问题说明

在Linux环境下运行Auto-Clock时，可能会遇到以下错误：
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "/path/to/cv2/qt/plugins" even though it was found.
This application failed to start because no Qt platform plugin could be initialized.
```

这个错误是因为缺少必要的图形界面依赖库。

## 解决方案

### 方案1：安装必要的图形界面依赖（推荐）

在Ubuntu/Debian系统上，运行以下命令安装必要的依赖：

```bash
sudo apt-get update
sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0 libxcb1-dev libx11-dev libxkbcommon-x11-0 libegl1-mesa-dev libgl1-mesa-glx libfontconfig1-dev libicu-dev libsqlite3-dev libxss1 libgconf-2-4 libxtst6 libasound2-dev libpulse-dev
```

在CentOS/RHEL/Fedora系统上，运行以下命令：

```bash
sudo yum install -y libX11-devel libXext-devel libXtst-devel libxcb-devel mesa-libGL-devel libxkbcommon-devel libXcursor-devel libXi-devel
```

### 方案2：使用无头模式

如果不需要图形界面，可以使用无头模式运行程序：

```bash
python entry.py --headless --task_id=YOUR_TASK_ID
```

### 方案3：使用虚拟显示器

如果没有物理显示器，可以使用Xvfb（虚拟 framebuffer X服务器）：

```bash
# 安装Xvfb
sudo apt-get install -y xvfb

# 使用Xvfb运行程序
xvfb-run -a python entry.py
```

## 使用启动脚本

为了简化在Linux环境下的使用，我们提供了一个便捷的启动脚本 `run_linux.sh`：

### 脚本功能

- 自动安装依赖库
- 提供友好的命令行界面
- 支持图形模式和无头模式切换

### 使用方法

1. 首先给脚本添加执行权限：
   ```bash
   chmod +x run_linux.sh
   ```

2. 查看帮助信息：
   ```bash
   ./run_linux.sh --help
   ```

3. 安装依赖库：
   ```bash
   ./run_linux.sh --install
   ```

4. 启动图形界面：
   ```bash
   ./run_linux.sh --gui
   # 或者简单运行
   ./run_linux.sh
   ```

5. 使用无头模式执行任务：
   ```bash
   ./run_linux.sh --headless --task-id 12345
   ```

## 运行程序

### 图形界面模式

```bash
# 方法1：直接运行
python entry.py

# 方法2：使用启动脚本
./run_linux.sh --gui
```

### 无头模式

```bash
# 方法1：直接运行
python entry.py --headless --task_id=YOUR_TASK_ID

# 方法2：使用启动脚本
./run_linux.sh --headless --task-id YOUR_TASK_ID
```

### 任务模式

```bash
# 方法1：直接运行
python entry.py --task_id=YOUR_TASK_ID

# 方法2：使用启动脚本
./run_linux.sh --task-id YOUR_TASK_ID
```

### 使用虚拟显示器

```bash
# 方法1：直接运行
xvfb-run -a python entry.py

# 方法2：使用启动脚本
xvfb-run -a ./run_linux.sh --gui
```

## 注意事项

1. 如果在服务器环境中运行，建议使用无头模式或虚拟显示器方案
2. 确保已安装所有必要的Python依赖：`pip install -r requirements.txt`
3. 如果使用网络控制功能，可能需要sudo权限
4. 在Linux环境下，某些功能可能需要额外的配置或权限