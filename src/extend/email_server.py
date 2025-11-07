import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from src.utils.log import Log

def html_content(subject, message):
    content = f"""
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: "Microsoft YaHei", Arial, sans-serif;
          }}
          body {{
            background-color: #f5f7fa;
            padding: 20px 0;
          }}
          .email-card {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            overflow: hidden;
          }}
          .card-header {{
            background-color: #4299e1;
            color: #ffffff;
            padding: 16px 24px;
            font-size: 18px;
            font-weight: 600;
          }}
          .card-content {{
            padding: 24px;
            line-height: 1.8;
            color: #4a5568;
          }}
          .message-content {{
            margin: 16px 0;
            padding: 16px;
            background-color: #f8f9fa;
            border-left: 4px solid #4299e1;
            border-radius: 4px;
          }}
          .send-time {{
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid #e8f4f8;
            color: #94a3b8;
            font-size: 14px;
            text-align: right;
          }}
          .footer-note {{
            padding: 16px 24px;
            background-color: #f8f9fa;
            color: #94a3b8;
            font-size: 12px;
            text-align: center;
            border-top: 1px solid #e8f4f8;
          }}
        </style>
      </head>
      <body>
        <div class="email-card">
          <div class="card-header">
            {subject}
          </div>
          <div class="card-content">
            <p>Auto Clock got a message for you:</p>
            <div class="message-content">
              {message}
            </div>
            <p>If you're unsure what this email is about, feel free to ignore it.</p>
            <div class="send-time">
              Send Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </div>
          </div>
          <div class="footer-note">
            This email is automatically sent by the system, please do not reply directly<br>All rights reserved © {datetime.now().year}
          </div>
        </div>
      </body>
    </html>
    """
    return content

def get_email_message(subject, title, message, sender_email, receiver_email):
    msg = MIMEText(html_content(f"{title}", f"{message}"), _subtype="html", _charset="utf-8")
    msg["From"] = formataddr(("Auto Clock", f"{sender_email}"))
    msg["To"] = Header(f"{receiver_email}", "utf-8")
    msg["Subject"] = Header(f"{subject}", "utf-8")
    return msg

def send_email(context):
    if context.get("smtp_server") is None or context.get("smtp_port") is None or context.get(
            "sender_email") is None or context.get("sender_auth_code") is None or context.get(
            "receiver_email") is None or context.get("message") is None or context.get("subject") is None or context.get("title") is None:
        message = "Empty context!"
        return False, message
    try:
        message = get_email_message(context.get("subject"), context.get("title"), context.get("message"), context.get("sender_email"), context.get("receiver_email"))

        server = smtplib.SMTP_SSL(context.get("smtp_server"), context.get("smtp_port"))
        server.login(context.get("sender_email"), context.get("sender_auth_code"))
        server.sendmail(context.get("sender_email"), context.get("receiver_email"), message.as_string())
        Log.info("HTML Email Send Success!")
        server.quit()
        return True, None
    except Exception as e:
        Log.error(f"HTML Email Send Failed: {str(e)}")
        return False, str(e)

def send_email_by_auto_clock(receiver_email, subject, title, message):
    email_info = {
        "smtp_server": "smtp.163.com",
        "smtp_port": 465,
        "sender_email": "auto_clock@163.com",
        "sender_auth_code": "AXx9tT5cHZKUQXjS",
        "receiver_email": f"{receiver_email}",
        "subject": f"{subject}",
        "title": f"{title}",
        "message": f"{message}"
    }
    ret, error = send_email(email_info)
    return ret, error