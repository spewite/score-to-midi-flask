import os
import threading
import mimetypes
import base64
import tempfile # Para crear archivos temporales para la conversión de SVG a PNG
from flask import current_app

# Brevo (Sendinblue) SDK
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Intenta importar cairosvg para la conversión. Si no está disponible, la conversión fallará y se registrará.
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    # No es necesario current_app.logger aquí, ya que esto es a nivel de módulo.
    # El logger se usará más tarde si se intenta una conversión.

def _configure_brevo_api():
    """
    Configures and returns the Brevo API client instance.
    Se asegura de que la clave API esté presente.
    """
    configuration = sib_api_v3_sdk.Configuration()
    api_key = os.getenv('BREVO_API_KEY')
    if not api_key:
        current_app.logger.error("BREVO_API_KEY is not set in environment variables. Brevo API cannot be configured.")
        return None
    configuration.api_key['api-key'] = api_key
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def _send_email_via_brevo_sync(app_context, subject, html_content_body, attachment_path_original=None):
    """
    Synchronous function to send an email via Brevo API.
    This function is intended to be run in a separate thread.
    Utiliza el contexto de la aplicación Flask para logging y configuración.
    Convierte SVG a PNG para adjuntar si es necesario.
    """
    with app_context:
        api_instance = _configure_brevo_api()
        if not api_instance:
            current_app.logger.error("Brevo API instance could not be configured. Email not sent.")
            return

        sender_email = os.getenv('BREVO_SENDER_EMAIL')
        personal_email = os.getenv('MY_PERSONAL_EMAIL')

        if not sender_email:
            current_app.logger.error("BREVO_SENDER_EMAIL is not set. Email not sent.")
            return
        if not personal_email:
            current_app.logger.error("MY_PERSONAL_EMAIL is not set. Email not sent.")
            return

        sender = sib_api_v3_sdk.SendSmtpEmailSender(name="Score-to-Midi Notifier", email=sender_email)
        to = [sib_api_v3_sdk.SendSmtpEmailTo(email=personal_email)]

        brevo_attachments = []
        path_to_attach_for_api = None
        filename_for_api_attachment = None
        temp_png_path = None # Para la limpieza del archivo PNG temporal

        if attachment_path_original:
            original_filename = os.path.basename(attachment_path_original)
            
            if original_filename.lower().endswith('.svg'):
                if CAIROSVG_AVAILABLE:
                    current_app.logger.info(f"SVG attachment '{original_filename}' detected. Attempting conversion to PNG.")
                    try:
                        # Crear un archivo temporal para la salida PNG
                        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_png_file:
                            temp_png_path = temp_png_file.name
                        
                        # Convertir SVG a PNG
                        cairosvg.svg2png(url=attachment_path_original, write_to=temp_png_path, background_color='white')
                        
                        path_to_attach_for_api = temp_png_path
                        filename_for_api_attachment = os.path.splitext(original_filename)[0] + ".png"
                        current_app.logger.info(f"SVG '{original_filename}' converted to PNG '{filename_for_api_attachment}' for attachment.")
                    except Exception as e_convert:
                        current_app.logger.error(f"Failed to convert SVG '{original_filename}' to PNG: {e_convert}. Email will be sent without this attachment.")
                        # No adjuntar si la conversión falla. temp_png_path se limpiará si se creó.
                        if temp_png_path and os.path.exists(temp_png_path):
                            os.remove(temp_png_path) # Limpieza inmediata si la conversión falla
                        temp_png_path = None # Asegurarse de que no se intente limpiar de nuevo
                else:
                    current_app.logger.warning(f"SVG attachment '{original_filename}' found, but cairosvg library is not available. Cannot convert to PNG. Email will be sent without this attachment.")
            else:
                # Para formatos no SVG, usar el archivo original
                path_to_attach_for_api = attachment_path_original
                filename_for_api_attachment = original_filename

            if path_to_attach_for_api and filename_for_api_attachment:
                try:
                    with open(path_to_attach_for_api, 'rb') as f:
                        file_data = f.read()
                    encoded_content = base64.b64encode(file_data).decode('utf-8')
                    
                    brevo_attachments.append(sib_api_v3_sdk.SendSmtpEmailAttachment(
                        name=filename_for_api_attachment, 
                        content=encoded_content
                    ))
                    current_app.logger.info(f"Attachment '{filename_for_api_attachment}' prepared for Brevo email.")
                except FileNotFoundError:
                    current_app.logger.error(f"Attachment file not found at path: {path_to_attach_for_api}. Sending email without attachment.")
                except Exception as e_attach:
                    current_app.logger.error(f"Error preparing attachment '{filename_for_api_attachment}' for Brevo: {e_attach}. Sending email without attachment.")
        
        # Construye el objeto del email transaccional
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=to,
            subject=subject,
            html_content=html_content_body,
            attachment=brevo_attachments if brevo_attachments else None
        )

        try:
            current_app.logger.info(f"Attempting to send email via Brevo to {personal_email} with subject: '{subject}'")
            api_response = api_instance.send_transac_email(send_smtp_email)
            current_app.logger.info(f"Brevo email sent successfully! Message ID: {api_response.message_id if hasattr(api_response, 'message_id') else 'N/A'}")
        except ApiException as e:
            current_app.logger.error(f"Brevo API Exception when sending email: Status {e.status}, Reason {e.reason}")
            current_app.logger.error(f"Brevo API Exception body: {e.body}")
        except Exception as e_general:
            current_app.logger.error(f"An unexpected error occurred sending email via Brevo: {e_general}")
        finally:
            # Limpieza del archivo PNG temporal si se creó y usó para el adjunto
            if temp_png_path and path_to_attach_for_api == temp_png_path and os.path.exists(temp_png_path):
                try:
                    os.remove(temp_png_path)
                    current_app.logger.info(f"Temporary PNG file '{temp_png_path}' deleted.")
                except Exception as e_cleanup:
                    current_app.logger.error(f"Error deleting temporary PNG file '{temp_png_path}': {e_cleanup}")


def send_email_notification(subject, body, attachment_path=None):
    """
    Public function to be called from app.py.
    Sends an email notification using Brevo API in a separate thread
    to avoid blocking the main Flask request.
    The 'body' parameter is used as html_content for the email.
    """
    if not os.getenv('BREVO_API_KEY'):
        current_app.logger.warning("BREVO_API_KEY not found, skipping email notification.")
        return
        
    app_context = current_app.app_context()
    # El argumento 'body' se pasa como 'html_content_body' a la función síncrona
    # 'attachment_path' se pasa como 'attachment_path_original'
    thread = threading.Thread(target=_send_email_via_brevo_sync, args=(app_context, subject, body, attachment_path))
    thread.daemon = True
    thread.start()
    current_app.logger.info("Brevo email sending task initiated in a background thread.")

