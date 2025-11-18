#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件功能独立测试脚本
用于测试邮件发送功能，帮助定位问题

使用方法:
    python test_email.py
    或
    python test_email.py --receiver your_email@example.com
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目路径到sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.log import Log
from src.extend.email_server import send_email_by_auto_clock

def test_network_connectivity():
    """测试网络连接"""
    import socket
    import requests
    
    print("\n" + "=" * 60)
    print("测试1: 网络连接性")
    print("=" * 60)
    
    # 测试DNS解析
    print("\n1.1 测试DNS解析...")
    try:
        ip = socket.gethostbyname("smtp.163.com")
        print(f"✓ DNS解析成功: smtp.163.com -> {ip}")
    except Exception as e:
        print(f"✗ DNS解析失败: {e}")
        return False
    
    # 测试SMTP端口连接
    print("\n1.2 测试SMTP端口连接...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.163.com', 465))
        sock.close()
        if result == 0:
            print("✓ SMTP端口465连接成功")
        else:
            print(f"✗ SMTP端口465连接失败，错误码: {result}")
            return False
    except Exception as e:
        print(f"✗ SMTP端口连接测试失败: {e}")
        return False
    
    # 测试HTTP连接
    print("\n1.3 测试HTTP连接...")
    try:
        response = requests.get("https://www.baidu.com", timeout=10)
        print(f"✓ HTTP连接成功，状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ HTTP连接失败: {e}")
        return False
    
    # 测试ipinfo.io
    print("\n1.4 测试ipinfo.io连接...")
    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
        data = response.json()
        print(f"✓ ipinfo.io连接成功")
        print(f"  IP: {data.get('ip')}")
        print(f"  位置: {data.get('city')}, {data.get('region')}, {data.get('country')}")
    except Exception as e:
        print(f"✗ ipinfo.io连接失败: {e}")
        print("  注意: 这不影响邮件发送，但会影响IP信息获取")
    
    print("\n✓ 网络连接性测试通过")
    return True

def test_smtp_connection():
    """测试SMTP连接和登录"""
    import smtplib
    
    print("\n" + "=" * 60)
    print("测试2: SMTP服务器连接和登录")
    print("=" * 60)
    
    smtp_server = "smtp.163.com"
    smtp_port = 465
    sender_email = "auto_clock@163.com"
    sender_auth_code = "AXx9tT5cHZKUQXjS"
    
    print(f"\nSMTP服务器: {smtp_server}:{smtp_port}")
    print(f"发件人: {sender_email}")
    
    try:
        print("\n2.1 连接SMTP服务器...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
        print("✓ SMTP服务器连接成功")
        
        print("\n2.2 登录SMTP服务器...")
        server.login(sender_email, sender_auth_code)
        print("✓ SMTP服务器登录成功")
        
        print("\n2.3 关闭连接...")
        server.quit()
        print("✓ 连接关闭成功")
        
        print("\n✓ SMTP连接和登录测试通过")
        return True
    except Exception as e:
        import traceback
        print(f"\n✗ SMTP测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        print(f"详细错误:\n{traceback.format_exc()}")
        return False

def test_send_email(receiver_email):
    """测试发送邮件"""
    print("\n" + "=" * 60)
    print("测试3: 发送测试邮件")
    print("=" * 60)
    
    print(f"\n收件人: {receiver_email}")
    
    # 构建测试邮件内容
    subject = "TEST EMAIL"
    title = "测试邮件 - Auto Clock Email Test"
    hello = "这是一封测试邮件，用于验证邮件发送功能是否正常。"
    message = f"""
    <table border="0" cellspacing="3" cellpadding="0" style="display: inline-table;">
      <tr>
        <td style="text-align: left; font-weight: normal; padding-right: 8px;">测试时间:</td>
        <td>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
      </tr>
      <tr>
        <td style="text-align: left; font-weight: normal; padding-right: 8px;">测试项目:</td>
        <td>Auto Clock 邮件功能测试</td>
      </tr>
      <tr>
        <td style="text-align: left; font-weight: normal; padding-right: 8px;">测试状态:</td>
        <td>如果您收到此邮件，说明邮件功能正常</td>
      </tr>
    </table>
    """
    
    print("\n3.1 开始发送邮件...")
    try:
        ret, error = send_email_by_auto_clock(
            receiver_email=receiver_email,
            subject=subject,
            title=title,
            hello=hello,
            message=message,
            ok=True
        )
        
        if ret:
            print("\n✓ 邮件发送成功！")
            print(f"请检查收件箱: {receiver_email}")
            return True
        else:
            print(f"\n✗ 邮件发送失败: {error}")
            return False
    except Exception as e:
        import traceback
        print(f"\n✗ 邮件发送异常: {e}")
        print(f"详细错误:\n{traceback.format_exc()}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Auto-Clock 邮件功能测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--receiver",
        default="suchinfinity@qq.com",
        help="收件人邮箱地址 (默认: suchinfinity@qq.com)"
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="跳过网络连接测试"
    )
    parser.add_argument(
        "--skip-smtp",
        action="store_true",
        help="跳过SMTP连接测试"
    )
    
    args = parser.parse_args()
    
    # 打开日志
    Log.open()
    
    print("\n" + "=" * 60)
    print("Auto-Clock 邮件功能测试")
    print("=" * 60)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"收件人: {args.receiver}")
    
    # 测试结果
    results = {}
    
    # 测试1: 网络连接
    if not args.skip_network:
        results['network'] = test_network_connectivity()
    else:
        print("\n跳过网络连接测试")
        results['network'] = None
    
    # 测试2: SMTP连接
    if not args.skip_smtp:
        results['smtp'] = test_smtp_connection()
    else:
        print("\n跳过SMTP连接测试")
        results['smtp'] = None
    
    # 测试3: 发送邮件
    results['email'] = test_send_email(args.receiver)
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if results.get('network') is not None:
        status = "✓ 通过" if results['network'] else "✗ 失败"
        print(f"\n网络连接测试: {status}")
    
    if results.get('smtp') is not None:
        status = "✓ 通过" if results['smtp'] else "✗ 失败"
        print(f"SMTP连接测试: {status}")
    
    status = "✓ 通过" if results['email'] else "✗ 失败"
    print(f"邮件发送测试: {status}")
    
    # 总体结果
    all_passed = all(v for v in results.values() if v is not None)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！邮件功能正常")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 部分测试失败，请查看上面的详细错误信息")
        print("=" * 60)
        print("\n故障排查建议:")
        if results.get('network') is False:
            print("  1. 检查网络连接是否正常")
            print("  2. 检查DNS配置 (cat /etc/resolv.conf)")
            print("  3. 尝试: ping smtp.163.com")
        if results.get('smtp') is False:
            print("  1. 检查防火墙是否阻止了465端口")
            print("  2. 检查SMTP服务器地址和端口是否正确")
            print("  3. 检查授权码是否有效")
        if results.get('email') is False:
            print("  1. 查看详细日志文件")
            print("  2. 检查收件人邮箱地址是否正确")
    
    # 关闭日志
    Log.close()
    
    # 返回退出码
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
