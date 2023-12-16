import random
import smtplib
from email.mime.text import MIMEText
import environ
import os
from pathlib import Path

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent
env.read_env(os.path.join(BASE_DIR, ".env"))


def send_otp_email(email,otp):
    gmail_user = env("EMAIL_ID")
    gmail_password = env("EMAIL_PASSWORD")  
    message = f'Your OTP is: {otp}'
    msg = MIMEText(message)
    msg['Subject'] = 'Your youngsta otp'
    msg['From'] = gmail_user
    msg['To'] = email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, email, msg.as_string())
        server.quit()
        return otp  

    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        return None