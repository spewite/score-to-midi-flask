import os
from email.message import EmailMessage
import smtplib

from flask import current_app

def send_email_notification(subject, body):
    """
    Sends an email using SMTP.
    """
    
    EMAIL_ADDRESS = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASS')
    PERSONAL_EMAIL = os.getenv('MY_PERSONAL_EMAIL')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = PERSONAL_EMAIL
    msg.set_content(body)
    
    try:
        # Using Gmail's SMTP server as an example
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        current_app.logger.info("Email notification sent successfully.")
    except Exception as e:
        current_app.logger.error(f"Failed to send email notification: {e}")