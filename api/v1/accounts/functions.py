import random
import smtplib
from email.mime.text import MIMEText
import environ
import os
from pathlib import Path
from django.contrib.auth.models import User, Group
import random
import string
from accounts.models import *

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
    

from django.contrib.auth.models import User, Group

def add_user_to_group(username, group_name):
    try:
        user = User.objects.get(username=username)
        print(f"User found: {user}")

        group, created = Group.objects.get_or_create(name=group_name)
        print(f"Group found: {group}")

        if created:
            print(f"Group '{group_name}' created successfully.")

        user.groups.add(group)
        print(f"User '{username}' added to group '{group_name}' successfully.")
        print(f"User '{username}' groups: {user.groups.all()}")

    except User.DoesNotExist:
        print(f"User '{username}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


def generate_referral_code():
        letters_and_digits = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(letters_and_digits) for i in range(6))
        while UserProfile.objects.filter(refferal_code=code).exists():
            code = ''.join(random.choice(letters_and_digits) for i in range(6))
        return code