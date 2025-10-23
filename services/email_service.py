"""
Email service for sending notifications, password resets, and verifications.
"""
from flask_mail import Mail, Message
from flask import current_app, render_template_string
import secrets
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Email will be initialized in app.py
mail = Mail()


def send_email(to, subject, body, html=None):
    """
    Send email using Flask-Mail.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text body
        html: Optional HTML body

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            body=body,
            html=html,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


def send_password_reset_email(user, reset_token):
    """
    Send password reset email to user.

    Args:
        user: User object
        reset_token: Password reset token

    Returns:
        True if sent successfully
    """
    reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5500')}/myapi/reset-password/{reset_token}"

    body = f"""
Hello {user.name},

You requested a password reset for your WHOIP account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this reset, please ignore this email.

Best regards,
WHOIP Team
    """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Password Reset Request</h2>
        <p>Hello {user.name},</p>
        <p>You requested a password reset for your WHOIP account.</p>
        <p>Click the button below to reset your password:</p>
        <a href="{reset_url}" class="button">Reset Password</a>
        <p>Or copy this link: <br><code>{reset_url}</code></p>
        <p><strong>This link will expire in 1 hour.</strong></p>
        <p>If you did not request this reset, please ignore this email.</p>
        <div class="footer">
            <p>Best regards,<br>WHOIP Team</p>
        </div>
    </div>
</body>
</html>
    """

    return send_email(
        to=user.email,
        subject="WHOIP - Password Reset Request",
        body=body,
        html=html
    )


def send_verification_email(user, verification_token):
    """
    Send email verification link to user.

    Args:
        user: User object
        verification_token: Email verification token

    Returns:
        True if sent successfully
    """
    verify_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5500')}/myapi/verify-email/{verification_token}"

    body = f"""
Hello {user.name},

Welcome to WHOIP! Please verify your email address.

Click the link below to verify your email:
{verify_url}

This link will expire in 24 hours.

Best regards,
WHOIP Team
    """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome to WHOIP!</h2>
        <p>Hello {user.name},</p>
        <p>Thank you for registering. Please verify your email address to activate your account.</p>
        <a href="{verify_url}" class="button">Verify Email</a>
        <p>Or copy this link: <br><code>{verify_url}</code></p>
        <p><strong>This link will expire in 24 hours.</strong></p>
        <div class="footer">
            <p>Best regards,<br>WHOIP Team</p>
        </div>
    </div>
</body>
</html>
    """

    return send_email(
        to=user.email,
        subject="WHOIP - Verify Your Email Address",
        body=body,
        html=html
    )


def send_token_approved_email(user, app_name):
    """
    Notify user when their API token is approved.

    Args:
        user: User object
        app_name: Name of approved application

    Returns:
        True if sent successfully
    """
    body = f"""
Hello {user.name},

Good news! Your API token for "{app_name}" has been approved.

You can now use this token to access the WHOIP API.

View your tokens: {current_app.config.get('BASE_URL', 'http://localhost:5500')}/myapi/tokens/

Best regards,
WHOIP Team
    """

    return send_email(
        to=user.email,
        subject=f"WHOIP - API Token Approved: {app_name}",
        body=body
    )


def send_rate_limit_warning(user, app_name, usage_percent):
    """
    Warn user when approaching rate limit.

    Args:
        user: User object
        app_name: Application name
        usage_percent: Percentage of rate limit used

    Returns:
        True if sent successfully
    """
    body = f"""
Hello {user.name},

Your API token "{app_name}" has used {usage_percent}% of its daily rate limit.

You may want to monitor your usage or request a limit increase.

View usage: {current_app.config.get('BASE_URL', 'http://localhost:5500')}/myapi/tokens/

Best regards,
WHOIP Team
    """

    return send_email(
        to=user.email,
        subject=f"WHOIP - Rate Limit Warning: {app_name}",
        body=body
    )
