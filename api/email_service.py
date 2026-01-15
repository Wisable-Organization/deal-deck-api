"""
Email service for sending transactional emails using AWS SES SMTP
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """
    Send password reset email using AWS SES SMTP
    
    Args:
        to_email: Recipient email address
        reset_link: Password reset link with token
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    from_email = os.getenv("EMAIL_FROM_ADDRESS")
    if not from_email:
        logger.error("EMAIL_FROM_ADDRESS environment variable not set")
        return False
    
    # In development, just log the email
    environment = os.getenv("ENVIRONMENT", "production")
    if environment.lower() in ["dev", "development"]:
        logger.info(f"[DEV] Password reset email would be sent to {to_email}")
        logger.info(f"[DEV] Reset link: {reset_link}")
        return True
    
    # Get SMTP configuration
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not all([smtp_host, smtp_username, smtp_password]):
        logger.error("SMTP configuration incomplete. Required: SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset Your Password - Deal Deck"
        msg["From"] = from_email
        msg["To"] = to_email
        
        # Email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
                <h1 style="color: #2c3e50; margin-top: 0;">Password Reset Request</h1>
                <p>You requested to reset your password for your Deal Deck account.</p>
                <p>Click the button below to reset your password. This link will expire in 24 hours.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Reset Password</a>
                </div>
                <p style="color: #666; font-size: 14px;">If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="color: #666; font-size: 12px; word-break: break-all;">{reset_link}</p>
                <p style="color: #666; font-size: 14px; margin-top: 30px;">If you didn't request this password reset, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Password Reset Request

You requested to reset your password for your Deal Deck account.

Click the link below to reset your password. This link will expire in 24 hours.

{reset_link}

If you didn't request this password reset, please ignore this email.
        """
        
        # Attach parts
        text_part = MIMEText(text_body, "plain")
        html_part = MIMEText(html_body, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email via SMTP
        if smtp_port == 465:
            # Use SSL for port 465
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            # Use STARTTLS for port 587 (or other ports)
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        
        logger.info(f"Password reset email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
        return False
