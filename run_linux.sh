#!/bin/bash

# Auto-Clock Linux启动脚本

# 检查是否提供了参数
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Auto-Clock Linux启动脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 [选项] [参数]"
    echo ""
    echo "选项:"
    echo "  --gui         启动图形界面（默认）"
    echo "  --headless    以无头模式运行"
    echo "  --task-id ID  指定要执行的任务ID"
    echo "  --install     安装必要的依赖库"
    echo "  --help, -h    显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                           # 启动图形界面"
    echo "  $0 --headless --task-id 123  # 以无头模式执行任务"
    echo "  $0 --install                 # 安装依赖"
    exit 0
fi

# 检查是否需要安装依赖
if [ "$1" == "--install" ]; then
    echo "正在安装必要的依赖库..."
    if command -v apt-get > /dev/null 2>&1; then
        echo "检测到apt-get，正在安装Ubuntu/Debian依赖..."
        sudo apt-get update
        sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0 libxcb1-dev libx11-dev libxkbcommon-x11-0 libegl1-mesa-dev libgl1-mesa-glx libfontconfig1-dev libicu-dev libsqlite3-dev libxss1 libgconf-2-4 libxtst6 libasound2-dev libpulse-dev
    elif command -v yum > /dev/null 2>&1; then
        echo "检测到yum，正在安装CentOS/RHEL/Fedora依赖..."
        sudo yum install -y libX11-devel libXext-devel libXtst-devel libxcb-devel mesa-libGL-devel libxkbcommon-devel libXcursor-devel libXi-devel
    else
        echo "无法识别的包管理器，请手动安装依赖库。"
        echo "请参考LINUX_INSTALL_GUIDE.md文件获取更多信息。"
        exit 1
    fi
    echo "依赖安装完成！"
    exit 0
fi

# 解析命令行参数
GUI_MODE=true
TASK_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --gui)
            GUI_MODE=true
            shift
            ;;
        --headless)
            GUI_MODE=false
            shift
            ;;
        --task-id)
            TASK_ID="$2"
            shift 2
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 构建Python命令
PYTHON_CMD="python3 entry.py"

if [ "$GUI_MODE" = false ]; then
    PYTHON_CMD="$PYTHON_CMD --headless"
fi

if [ -n "$TASK_ID" ]; then
    PYTHON_CMD="$PYTHON_CMD --task_id $TASK_ID"
fi

echo "正在运行: $PYTHON_CMD"
eval $PYTHON_CMD