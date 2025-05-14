import os
import mimetypes
from email.message import EmailMessage
import smtplib
import threading # Importar threading
from flask import current_app

def _send_email_sync(app_context, subject, body, attachment_path=None):
    """
    Función síncrona real que envía el email.
    Necesita el contexto de la aplicación para acceder a current_app.logger.
    """
    with app_context: # Asegura que current_app.logger funcione dentro del hilo
        EMAIL_ADDRESS = os.getenv('EMAIL_USER')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASS')
        PERSONAL_EMAIL = os.getenv('MY_PERSONAL_EMAIL')

        if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not PERSONAL_EMAIL:
            current_app.logger.error("Email environment variables (EMAIL_USER, EMAIL_PASS, MY_PERSONAL_EMAIL) are not set. Email not sent.")
            return

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = PERSONAL_EMAIL # Asegúrate que esta variable esté configurada
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
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20) as smtp: # Timeout de 20s para la conexión
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
            current_app.logger.info("Email notification sent successfully (via thread).")
        except smtplib.SMTPAuthenticationError as e:
            current_app.logger.error(f"SMTP Authentication Error for email: {e}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email notification (via thread): {e}")
            current_app.logger.error(f"Exception type: {type(e)}")


def send_email_notification(subject, body, attachment_path=None):
    """
    Sends an email in a separate thread to avoid blocking the main request.
    """
    # current_app no está disponible directamente si se llama desde fuera de un contexto de request,
    # pero aquí se llama desde un request, así que está bien.
    # Pasamos el contexto de la aplicación al hilo.
    app_context = current_app.app_context()
    thread = threading.Thread(target=_send_email_sync, args=(app_context, subject, body, attachment_path))
    thread.daemon = True # Permite que la aplicación principal termine incluso si los hilos están corriendo
    thread.start()
    current_app.logger.info("Email sending task started in a background thread.")