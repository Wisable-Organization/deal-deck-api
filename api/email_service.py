"""
Email service for sending transactional emails using AWS SES
"""
import os
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

# Initialize SES client
ses_client = None

def get_ses_client():
    """Get or create SES client"""
    global ses_client
    if ses_client is None:
        aws_region = os.getenv("AWS_REGION", "us-east-2")
        ses_client = boto3.client("ses", region_name=aws_region)
    return ses_client


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """
    Send password reset email using AWS SES
    
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
    
    try:
        client = get_ses_client()
        
        # Email subject and body
        subject = "Reset Your Password - Deal Deck"
        
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
        
        # Send email via SES
        response = client.send_email(
            Source=from_email,
            Destination={
                "ToAddresses": [to_email]
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": text_body,
                        "Charset": "UTF-8"
                    },
                    "Html": {
                        "Data": html_body,
                        "Charset": "UTF-8"
                    }
                }
            }
        )
        
        logger.info(f"Password reset email sent successfully to {to_email}. MessageId: {response['MessageId']}")
        return True
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"AWS SES error sending email to {to_email}: {error_code} - {error_message}")
        return False
    except BotoCoreError as e:
        logger.error(f"Boto3 error sending email to {to_email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
        return False
