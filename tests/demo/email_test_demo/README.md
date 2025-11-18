# 邮件功能测试工具

这个目录包含用于测试Auto-Clock邮件发送功能的独立测试脚本。

## 文件说明

- **`test_email.py`** - 邮件功能测试脚本
- **`EMAIL_TEST_GUIDE.md`** - 详细的使用指南和故障排查文档

## 快速使用

```bash
# 从项目根目录运行
cd /path/to/auto-clock

# 运行测试（使用默认收件人）
python3 tests/demo/email_test_demo/test_email.py

# 指定收件人
python3 tests/demo/email_test_demo/test_email.py --receiver your_email@example.com
```

## 测试内容

1. **网络连接性测试** - DNS解析、SMTP端口、HTTP连接
2. **SMTP服务器测试** - 连接和登录验证
3. **邮件发送测试** - 实际发送测试邮件

## 详细文档

查看 [EMAIL_TEST_GUIDE.md](./EMAIL_TEST_GUIDE.md) 获取完整的使用说明和故障排查指南。

## 注意事项

- 测试脚本需要从项目根目录运行，或确保Python能找到 `src` 模块
- 测试过程会生成日志文件在 `~/.local/share/auto-clock/log/`
- 默认使用 `auto_clock@163.com` 作为发件人（需要有效的授权码）
