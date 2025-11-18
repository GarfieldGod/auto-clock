# Linux打包兼容性指南

## 问题说明

在Linux上使用PyInstaller打包的应用可能遇到GLIBC版本不兼容问题：

```
Failed to load Python shared library: version `GLIBC_2.35' not found
```

## 原因分析

- **打包环境**：在较新的Linux系统上打包（如Ubuntu 22.04，GLIBC 2.35）
- **运行环境**：在较旧的Linux系统上运行（如Ubuntu 20.04，GLIBC 2.31）
- **结果**：应用无法运行，因为依赖的GLIBC版本不存在

## 解决方案

### 方案1：在目标最低版本系统上打包（推荐）

**原则**：在用户可能使用的**最低版本**Linux系统上打包。

#### 各Linux版本的GLIBC版本

| 发行版 | 版本 | GLIBC版本 |
|--------|------|-----------|
| Ubuntu 18.04 | Bionic | 2.27 |
| Ubuntu 20.04 | Focal | 2.31 |
| Ubuntu 22.04 | Jammy | 2.35 |
| Ubuntu 24.04 | Noble | 2.39 |
| Debian 10 | Buster | 2.28 |
| Debian 11 | Bullseye | 2.31 |
| CentOS 7 | - | 2.17 |
| CentOS 8 | - | 2.28 |

#### 建议打包环境

- **推荐**：Ubuntu 20.04（GLIBC 2.31）
- **兼容性**：可在 Ubuntu 20.04+ 和大多数现代Linux发行版上运行

#### 操作步骤

```bash
# 1. 准备Ubuntu 20.04环境（虚拟机或Docker）
# 2. 安装依赖
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# 3. 克隆项目
git clone <your-repo>
cd auto-clock

# 4. 安装Python依赖
pip3 install -r requirements.txt
pip3 install pyinstaller

# 5. 打包
./build_linux.sh
```

### 方案2：使用Docker打包（最佳实践）

使用Docker可以确保在固定的环境中打包，避免环境差异。

#### 使用方法

```bash
# 1. 确保已安装Docker
docker --version

# 2. 给脚本添加执行权限
chmod +x docker_build.sh

# 3. 运行Docker打包
./docker_build.sh
```

#### Docker打包的优势

- ✓ 环境一致性：始终在Ubuntu 20.04环境中打包
- ✓ 可重复性：每次打包结果一致
- ✓ 隔离性：不影响主机环境
- ✓ 便携性：可以在任何安装了Docker的系统上打包

### 方案3：静态链接（高级）

修改 `pack_linux.spec`，尝试静态链接：

```python
# 在 pack_linux.spec 中添加
a = Analysis(
    ...
    excludes=['_tkinter'],  # 排除不需要的模块
)

exe = EXE(
    ...
    strip=True,  # 启用strip
    upx=True,    # 启用UPX压缩
)
```

### 方案4：提供源码运行方式

对于无法解决兼容性的情况，提供源码运行方式：

```bash
# 用户端安装
git clone <your-repo>
cd auto-clock
pip3 install -r requirements.txt

# 运行
python3 entry.py
```

## 检查GLIBC版本

### 检查系统GLIBC版本

```bash
# 方法1
ldd --version

# 方法2
/lib/x86_64-linux-gnu/libc.so.6

# 方法3
getconf GNU_LIBC_VERSION
```

### 检查可执行文件依赖的GLIBC版本

```bash
# 查看依赖
ldd dist/auto_clock

# 查看需要的GLIBC版本
objdump -T dist/auto_clock | grep GLIBC | sed 's/.*GLIBC_\([.0-9]*\).*/\1/g' | sort -Vu
```

## 测试兼容性

### 在不同系统上测试

建议在以下系统上测试打包后的应用：

1. **Ubuntu 20.04**（最低支持版本）
2. **Ubuntu 22.04**（常用版本）
3. **Ubuntu 24.04**（最新LTS版本）
4. **Debian 11**（服务器常用）

### 使用Docker测试

```bash
# 测试在Ubuntu 20.04上运行
docker run --rm -v $(pwd)/dist:/app ubuntu:20.04 /app/auto_clock --help

# 测试在Ubuntu 22.04上运行
docker run --rm -v $(pwd)/dist:/app ubuntu:22.04 /app/auto_clock --help

# 测试在Debian 11上运行
docker run --rm -v $(pwd)/dist:/app debian:11 /app/auto_clock --help
```

## 常见错误及解决

### 错误1: GLIBC版本不匹配

```
version `GLIBC_2.35' not found
```

**解决**：在较旧的系统上重新打包（如Ubuntu 20.04）

### 错误2: libpython找不到

```
Failed to load Python shared library
```

**解决**：
```bash
# 检查Python版本
python3 --version

# 重新安装Python开发包
sudo apt-get install python3-dev
```

### 错误3: Qt库缺失

```
qt.qpa.plugin: Could not load the Qt platform plugin
```

**解决**：
```bash
# 安装Qt依赖
sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0
```

## 分发建议

### 方式1：提供多个版本

为不同的Linux发行版提供不同的打包版本：

```
auto_clock_ubuntu20.04_x64
auto_clock_ubuntu22.04_x64
auto_clock_debian11_x64
```

### 方式2：提供AppImage

AppImage是一种更通用的Linux应用分发格式：

```bash
# 安装appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# 创建AppImage
./appimagetool-x86_64.AppImage dist/ auto_clock.AppImage
```

### 方式3：提供安装脚本

```bash
#!/bin/bash
# install.sh

echo "检测系统版本..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "系统: $NAME $VERSION"
fi

echo "检测GLIBC版本..."
GLIBC_VERSION=$(ldd --version | head -n1 | grep -oP '\d+\.\d+$')
echo "GLIBC版本: $GLIBC_VERSION"

# 根据版本选择合适的二进制文件
if [ "$(printf '%s\n' "2.31" "$GLIBC_VERSION" | sort -V | head -n1)" = "2.31" ]; then
    echo "使用Ubuntu 20.04版本"
    cp auto_clock_ubuntu20 auto_clock
else
    echo "使用源码运行方式"
    pip3 install -r requirements.txt
fi
```

## 推荐方案总结

1. **开发阶段**：使用Docker打包，确保环境一致
2. **测试阶段**：在多个Linux版本上测试
3. **分发阶段**：
   - 提供Ubuntu 20.04版本（最大兼容性）
   - 提供源码运行方式（备选方案）
   - 在README中说明系统要求

## 系统要求示例

在README中添加：

```markdown
## 系统要求

- Linux发行版：Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- GLIBC版本：2.31+
- Python版本：3.8+（仅源码运行需要）

检查GLIBC版本：
\`\`\`bash
ldd --version
\`\`\`

如果GLIBC版本低于2.31，请使用源码运行方式。
```
