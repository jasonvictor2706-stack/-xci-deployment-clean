import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", "AgriSen <noreply@agrisen.com>")

def send_otp_email(email: str, otp_code: str):
    if not SMTP_USER or not SMTP_PASSWORD or SMTP_USER.startswith("dummy"):
        print(f"\n========================================")
        print(f"[SIMULATED EMAIL] OTP for {email} is: {otp_code}")
        print(f"========================================\n")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = email
        msg['Subject'] = "Your AgriSen Login OTP"

        body = f"Your verification code is: {otp_code}\nThis OTP expires in 10 minutes."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")
        # Fallback to simulated email locally if real credentials fail
        print(f"[SIMULATED EMAIL] OTP for {email} is: {otp_code}")
