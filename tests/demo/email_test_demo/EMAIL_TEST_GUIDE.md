# 邮件功能测试指南

本指南介绍如何使用 `test_email.py` 脚本测试邮件发送功能。

## 快速开始

### 在Linux服务器上测试

```bash
# 1. 进入项目目录
cd /data/proj/auto-clock

# 2. 激活虚拟环境（如果有）
source .venv/bin/activate

# 3. 运行测试脚本（使用默认收件人）
python3 test_email.py

# 4. 或指定收件人
python3 test_email.py --receiver your_email@example.com
```

## 测试内容

脚本会依次执行以下测试：

### 测试1: 网络连接性
- DNS解析测试 (smtp.163.com)
- SMTP端口465连接测试
- HTTP连接测试 (baidu.com)
- ipinfo.io API测试

### 测试2: SMTP服务器连接
- 连接smtp.163.com:465
- 使用授权码登录
- 验证连接是否正常

### 测试3: 发送测试邮件
- 构建HTML邮件
- 发送到指定收件人
- 验证发送结果

## 命令行选项

```bash
# 查看帮助
python3 test_email.py --help

# 指定收件人
python3 test_email.py --receiver your_email@example.com

# 跳过网络连接测试
python3 test_email.py --skip-network

# 跳过SMTP连接测试
python3 test_email.py --skip-smtp

# 组合使用
python3 test_email.py --receiver test@qq.com --skip-network
```

## 输出说明

### 成功输出示例
```
==============================================================
测试1: 网络连接性
==============================================================

1.1 测试DNS解析...
✓ DNS解析成功: smtp.163.com -> 220.181.12.16

1.2 测试SMTP端口连接...
✓ SMTP端口465连接成功

✓ 网络连接性测试通过

==============================================================
测试2: SMTP服务器连接和登录
==============================================================

2.1 连接SMTP服务器...
✓ SMTP服务器连接成功

2.2 登录SMTP服务器...
✓ SMTP服务器登录成功

✓ SMTP连接和登录测试通过

==============================================================
测试3: 发送测试邮件
==============================================================

3.1 开始发送邮件...
✓ 邮件发送成功！

==============================================================
✓ 所有测试通过！邮件功能正常
==============================================================
```

### 失败输出示例
```
1.1 测试DNS解析...
✗ DNS解析失败: [Errno -3] Temporary failure in name resolution

故障排查建议:
  1. 检查网络连接是否正常
  2. 检查DNS配置 (cat /etc/resolv.conf)
  3. 尝试: ping smtp.163.com
```

## 常见问题排查

### 问题1: DNS解析失败
```bash
# 检查DNS配置
cat /etc/resolv.conf

# 测试DNS解析
nslookup smtp.163.com
ping smtp.163.com

# 临时修改DNS（如果需要）
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

### 问题2: SMTP端口连接失败
```bash
# 测试端口连接
telnet smtp.163.com 465
nc -zv smtp.163.com 465

# 检查防火墙
sudo iptables -L -n | grep 465
sudo firewall-cmd --list-all

# 检查网络路由
traceroute smtp.163.com
```

### 问题3: 登录失败
- 检查授权码是否正确
- 确认163邮箱已开启SMTP服务
- 检查是否被163服务器限流

### 问题4: 发送失败但连接正常
- 检查收件人邮箱地址是否正确
- 查看详细日志文件
- 检查邮件内容是否符合规范

## 日志文件

测试过程中会生成详细的日志文件，位于：
```
~/.local/share/auto-clock/log/
```

查看最新日志：
```bash
ls -lt ~/.local/share/auto-clock/log/ | head -5
tail -f ~/.local/share/auto-clock/log/最新日志文件.log
```

## 在实际任务中查看日志

如果测试脚本正常但实际任务失败，可以查看任务执行时的日志：

```bash
# 查看最近的日志文件
cd ~/.local/share/auto-clock/log/
ls -lt | head -10

# 查看具体日志内容
cat 2025-11-18_16_58_01.399905.log

# 搜索错误信息
grep -i "error" *.log
grep -i "email" *.log
```

## 网络环境检查

### 检查网络连接
```bash
# 检查网络接口
ip addr show

# 检查网络连通性
ping -c 4 8.8.8.8
ping -c 4 baidu.com

# 检查DNS
nslookup smtp.163.com
dig smtp.163.com
```

### 检查时间同步
```bash
# SMTP可能对时间敏感
date
timedatectl status

# 如果时间不对，同步时间
sudo ntpdate ntp.aliyun.com
```

## 调试技巧

### 1. 增加等待时间
如果是网络连接时机问题，可以在 `entry.py` 中增加等待时间：
```python
# 当前是5秒，可以尝试增加到10秒
time.sleep(10)
```

### 2. 手动测试SMTP
```python
import smtplib

server = smtplib.SMTP_SSL("smtp.163.com", 465, timeout=30)
server.set_debuglevel(1)  # 开启调试模式
server.login("auto_clock@163.com", "AXx9tT5cHZKUQXjS")
server.quit()
```

### 3. 检查Python环境
```bash
# 检查Python版本
python3 --version

# 检查已安装的包
pip list | grep -i smtp
pip list | grep -i email
```

## 联系支持

如果问题仍未解决，请提供以下信息：
1. 测试脚本的完整输出
2. 日志文件内容
3. 网络环境信息 (`ip addr`, `cat /etc/resolv.conf`)
4. Python版本和系统信息
