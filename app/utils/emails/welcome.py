import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from fastapi import HTTPException

def send_welcome_email(email: str, username: str, verification_link: str):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Welcome to FinanceApp - Complete Your Registration 🚀"
    msg['From'] = os.getenv('FROM_EMAIL')
    msg['To'] = email

    text = f"""\
    Welcome to FinanceApp!

    Hello {username},

    We're excited to have you onboard! Please verify your email by clicking:
    {verification_link}

    If you didn't request this, please ignore this email.
    """

    html = f"""\
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h1 style="color: #2c3e50;">Welcome to FinanceApp!</h1>
        <p>Hello {username},</p>
        <p>We're excited to have you onboard!</p>
        <p>
          <a href="{verification_link}" 
             style="background-color: #3498db; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">
            Verify Your Email
          </a>
        </p>
        <p><small>If you didn't request this, please ignore this email.</small></p>
      </body>
    </html>
    """

    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP(os.getenv('MAILTRAP_HOST'), int(os.getenv('MAILTRAP_PORT'))) as server:
            server.starttls() 
            server.login(os.getenv('MAILTRAP_USERNAME'), os.getenv('MAILTRAP_PASSWORD'))
            server.send_message(msg)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email sending failed: {str(e)}"
        )