"""
Servicio de envío de emails usando Resend
"""
import resend
from app.config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para enviar emails usando Resend API"""

    def __init__(self):
        """Inicializa el servicio con la API key de Resend"""
        resend.api_key = settings.resend_api_key

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Envía email de recuperación de contraseña

        Args:
            to_email: Email del destinatario
            reset_token: Token de recuperación

        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            # Construir URL de recuperación
            reset_url = f"{settings.frontend_url}/reset-password.html?token={reset_token}"

            # HTML del email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: #f9f9f9;
                        padding: 30px;
                        border-radius: 0 0 5px 5px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        font-size: 12px;
                        color: #666;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffc107;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 15px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎮 PlayZone Inventory</h1>
                    </div>
                    <div class="content">
                        <h2>Recuperación de Contraseña</h2>
                        <p>Hola,</p>
                        <p>Recibimos una solicitud para restablecer tu contraseña. Haz clic en el botón de abajo para crear una nueva contraseña:</p>

                        <div style="text-align: center;">
                            <a href="{reset_url}" class="button">Restablecer Contraseña</a>
                        </div>

                        <div class="warning">
                            <strong>⏰ Importante:</strong> Este enlace expirará en {settings.reset_token_expire_minutes} minutos.
                        </div>

                        <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este correo de forma segura.</p>

                        <p><small>Si el botón no funciona, copia y pega este enlace en tu navegador:</small></p>
                        <p><small>{reset_url}</small></p>
                    </div>
                    <div class="footer">
                        <p>© 2025 PlayZone Inventory System</p>
                        <p>Este es un correo automático, por favor no respondas.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Enviar email
            params = {
                "from": settings.email_from,
                "to": [to_email],
                "subject": "🔐 Recuperación de Contraseña - PlayZone",
                "html": html_content
            }

            response = resend.Emails.send(params)

            print(f"\n{'='*60}")
            print(f"✅ EMAIL DE RECUPERACIÓN ENVIADO EXITOSAMENTE")
            print(f"{'='*60}")
            print(f"📧 Destinatario: {to_email}")
            print(f"📋 Response ID: {response.get('id', 'N/A')}")
            print(f"🔗 Reset URL: {reset_url}")
            print(f"{'='*60}\n")

            logger.info(f"Email de recuperación enviado a {to_email}")
            logger.debug(f"Resend response: {response}")

            return True

        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ ERROR AL ENVIAR EMAIL DE RECUPERACIÓN")
            print(f"{'='*60}")
            print(f"📧 Destinatario: {to_email}")
            print(f"⚠️  Error: {str(e)}")
            print(f"{'='*60}\n")

            logger.error(f"Error al enviar email de recuperación: {str(e)}")
            return False

    def send_password_changed_notification(self, to_email: str) -> bool:
        """
        Envía notificación de que la contraseña fue cambiada

        Args:
            to_email: Email del destinatario

        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: #f9f9f9;
                        padding: 30px;
                        border-radius: 0 0 5px 5px;
                    }}
                    .success {{
                        background-color: #d4edda;
                        border: 1px solid #c3e6cb;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 15px 0;
                        text-align: center;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffc107;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 15px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎮 PlayZone Inventory</h1>
                    </div>
                    <div class="content">
                        <h2>Contraseña Actualizada</h2>

                        <div class="success">
                            <h3>✅ Tu contraseña ha sido cambiada exitosamente</h3>
                        </div>

                        <p>Hola,</p>
                        <p>Te confirmamos que tu contraseña de PlayZone Inventory ha sido actualizada correctamente.</p>

                        <div class="warning">
                            <strong>⚠️ ¿No fuiste tú?</strong>
                            <p>Si no realizaste este cambio, contacta al administrador del sistema inmediatamente.</p>
                        </div>

                        <p>Ahora puedes iniciar sesión con tu nueva contraseña.</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 PlayZone Inventory System</p>
                        <p>Este es un correo automático, por favor no respondas.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            params = {
                "from": settings.email_from,
                "to": [to_email],
                "subject": "✅ Contraseña Actualizada - PlayZone",
                "html": html_content
            }

            response = resend.Emails.send(params)

            print(f"\n{'='*60}")
            print(f"✅ NOTIFICACIÓN DE CAMBIO ENVIADA EXITOSAMENTE")
            print(f"{'='*60}")
            print(f"📧 Destinatario: {to_email}")
            print(f"📋 Response ID: {response.get('id', 'N/A')}")
            print(f"{'='*60}\n")

            logger.info(f"Notificación de cambio de contraseña enviada a {to_email}")
            logger.debug(f"Resend response: {response}")

            return True

        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ ERROR AL ENVIAR NOTIFICACIÓN")
            print(f"{'='*60}")
            print(f"📧 Destinatario: {to_email}")
            print(f"⚠️  Error: {str(e)}")
            print(f"{'='*60}\n")

            logger.error(f"Error al enviar notificación de cambio de contraseña: {str(e)}")
            return False


# Instancia global del servicio
email_service = EmailService()
