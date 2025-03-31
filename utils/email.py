import os
import mimetypes
from email.message import EmailMessage
import smtplib

from flask import current_app

def send_email_notification(subject, body, attachment_path=None):
    """
    Sends an email using SMTP. Optionally attaches a file if attachment_path is provided.
    """
    
    EMAIL_ADDRESS = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASS')
    PERSONAL_EMAIL = os.getenv('MY_PERSONAL_EMAIL')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = PERSONAL_EMAIL
    msg.set_content(body)
    
    if attachment_path:
        try:
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
            file_name = os.path.basename(attachment_path)
            mime_type, _ = mimetypes.guess_type(attachment_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            maintype, subtype = mime_type.split('/', 1)
            msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
        except Exception as attach_err:
            current_app.logger.error(f"Failed to attach file: {attach_err}")
    
    try:
        # Using Gmail's SMTP server as an example
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        current_app.logger.info("Email notification sent successfully.")
    except Exception as e:
        current_app.logger.error(f"Failed to send email notification: {e}")